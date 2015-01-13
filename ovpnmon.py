import sys
import os
import logging
import select
import traceback
import win32serviceutil
import win32service
import win32event
from threading import Thread, Event

from viper.backend.bottle import ServerAdapter, run as bottle_run

from viper.backend import http
http.init()
__bottle_app__ = http.__app__

# Set host and port used to bind the webserver.  Leave the __host__ set to the
# empty string to bind to all interfaces.
__host__ = ''
__port__ = '8088'

## ###########################################################################
class WSGIRefHandleOneServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        import servicemanager
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        handler_class = WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            handler_class = QuietHandler
        srv = make_server(self.host, self.port, handler, handler_class=handler_class)
        servicemanager.LogInfoMsg("Bound to %s:%s" % (__host__ or '0.0.0.0', __port__))
        srv_wait = srv.fileno()
        # The default  .serve_forever() call blocks waiting for requests.
        # This causes the side effect of only shutting down the service if a
        # request is handled.
        #
        # To fix this, we use the one-request-at-a-time ".handle_request"
        # method.  Instead of sitting polling, we use select to sleep for a
        # second and still be able to handle the request.
        while self.options['notifyEvent'].isSet():
            ready = select.select([srv_wait], [], [], 1)
            if srv_wait in ready[0]:
                srv.handle_request()
            continue

class BottleWsgiServer(Thread):
    def __init__(self, eventNotifyObj):
        Thread.__init__(self)
        self.notifyEvent = eventNotifyObj

    def run ( self ):
        bottle_run(__bottle_app__, host=__host__, port=__port__, server=WSGIRefHandleOneServer, reloader=False,
                    quiet=True, notifyEvent=self.notifyEvent)

## ###########################################################################
class BottleService(win32serviceutil.ServiceFramework):
    """ Windows NT Service class for running a bottle.py server """

    _svc_name_ = "ovpnmon"
    _svc_display_name_ = "Viper monitor"
    _svc_description_ = "Guards your connection to the internet"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # Create an event which we will use to wait on.
        # The "service stop" request will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)


    def SvcStop(self):
        # Before we do anything, tell the SCM we are starting the stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # stop the process if necessary
        self.thread_event.clear()
        self.bottle_srv.join()

        # And set my event.
        win32event.SetEvent(self.hWaitStop)

    # SvcStop only gets triggered when the user explicitly stops (or restarts)
    # the service.  To shut the service down cleanly when Windows is shutting
    # down, we also need to hook SvcShutdown.
    SvcShutdown = SvcStop

    def SvcDoRun(self):
        import servicemanager

        # log a service started message
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ' (%s)' % self._svc_display_name_))

        while 1:
            self.thread_event = Event()
            self.thread_event.set()
            try:
                self.bottle_srv = BottleWsgiServer(self.thread_event)
                self.bottle_srv.start()
            except Exception as ex:
                logging.exception("Failed to start server process")
                servicemanager.LogErrorMsg(errmsg)
                self.SvcStop()

            rc = win32event.WaitForMultipleObjects((self.hWaitStop,), 0, win32event.INFINITE)
            if rc == win32event.WAIT_OBJECT_0:
                # user sent a stop service request
                self.SvcStop()
                break

        # log a service stopped message
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, ' (%s) ' % self._svc_display_name_))


if __name__=='__main__':
    win32serviceutil.HandleCommandLine(BottleService)
