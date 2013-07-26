
# windows 7 specific UTF-8 work-around
from tools import log
import codecs
codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

#log("Registering windows stream codecs for the utf-8 -> cp65001 problem...")