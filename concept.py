import http.client
import pickle
import datetime

class Space:
	# a tab or page (simulation), collection of concepts
	
	def __init__(self):
		self.id = ""
		self.name = ""
		self.concepts = []
		
		# Create some dummy data
		c = Concept()
		c.id = 0
		c.loc = (150,150)
		c.size = (100,80)
		c.name = "Test"
		c2 = Concept()
		c2.id = 1
		c2.loc = (350,50)
		c2.size = (100,80)
		c2.name = "Test 123"
		
		self.concepts.append(c)
		self.concepts.append(c2)
	
	def getConceptById(self, cId):
		for c in self.concepts:
			if int(c.id) == int(cId):
				return c
		return None
	
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
		
class EventRunner:
	def __init__(self):
		self.events = []
		self.queue = []
		self.maxRuns = 100
	
	def runDefault(self):
		self.events = []
		self.events.append("START")
		self.runEvents()
	
	def runEvents(self):
		# TODO: Timing and sharing data between concepts
		# Time (ticks) and events (conceptXHasFinished, etc)
		# (Check max runs, avoid loops)
		
		#for e in self.events:
		#	for i in self.queue:
		#		if i.triggerOnEvent(e):
		#			i.run()
		return True

class Log:
	def __init__(self):
		self.list = []
	
	def clear(self):
		self.list = []
	
	def info(self, text):
		self.list.append((datetime.datetime.now(), "INFO", text))
	
	def error(self, text):
		self.list.append((datetime.datetime.now(), "ERROR", text))
		
class Concept:
	def __init__(self):
		self.id = ""
		self.name = ""
		self.log = Log()
		self.loc = (0, 0)
		self.size = (100, 100) #Size, in px
		self.settings = {}
		
		self.triggerEvents = []
		
		self.reqInput  = []
		self.addInput = []
		self.reqOutput = []
		self.input = {}
		self.output = {}
		self.runTime = [None, None]
	
	def triggerOnEvent(self, event):
		if event in self.triggerEvents:
			return True
		return False
	
	def hasSetting(self, key):
		if key in self.settings:
			return True
		return False
	
	def getSetting(self, key):
		if key in self.settings:
			return self.settings[key]
		return None
	
	def setSetting(self, key, value):
		self.settings[key] = value
		return True
	
	def setInput(self, iKey, iVal):
		self.input[iKey] = iVal
		return True
		
	def getInput(self, iKey):
		return self.input[iKey]
	
	def getInputOrDefault(self, iKey, dVal):
		if(iKey in self.input):
			return self.input[iKey]
		return dVal
	
	def validateInput(self):
		for f in self.reqInput:
			if(not f in self.input):
				return False
		return True

	def validateOutput(self):
		for f in self.reqOutput:
			if(not f in self.output):
				return False
		return True
	
	def preRun(self):
		# clean input
		self.input = {}
		self.log.clear()
		self.runTime = [datetime.datetime.now(), None]
		
		for r in self.reqInput:
			# Read default from settings
			key = "input." + r
			if self.hasSetting(key):
				self.setInput(key, self.getSetting(key))
		
		for a in self.addInput:
			# Read additional fields if present
			key = "input." + a
			if self.hasSetting(key):
				self.setInput(key, self.getSetting(key))

		if(self.hasSetting("input.source")):
			# Copy input values from other concept
			source = self.getSetting("input.source")
			
			self.log.info("Copying input values from " + source)
			
			if(isinstance(source, Concept)):
				for f in source.output:
					self.setInput(f, source.output[f])
			
		if not self.validateInput():
			self.log.error("Could not validate input")
		
	def run(self):
		# validate required data present (always)
		# run the actual code
		# either py code, or through "eval"
		# input  = parameters for running
		# output = result from running
		
		# validate the output (always)
		
		return True

	def postRun(self):
		self.runTime[1] = datetime.datetime.now()
		self.log.info("Run time: " + str(self.runTime[1] - self.runTime[0]))
		
class HttpRequest(Concept):
	def __init__(self):
		Concept.__init__(self)
		self.reqInput = ["host", "path"]
	
	def run(self):
		con = 0
		
		if(self.getInputOrDefault("scheme", "http") == "https"):
			con = http.client.HTTPSConnection(self.getInput("host"), self.getInputOrDefault("port", 443), timeout=self.getInputOrDefault("timeout", 10))
		else:
			con = http.client.HTTPConnection(self.getInput("host"), self.getInputOrDefault("port", 80), timeout=self.getInputOrDefault("timeout", 10))
		
		# TODO: POST or GET
		con.request("GET", self.getInput("path"))
		r1 = con.getresponse()
		print(r1.status, r1.reason)
		con.close()
		
		return True

#h = HttpRequest()
#h.setSetting("input.scheme", "https")
#h.setSetting("input.host", "s.utv.vegvesen.no")
#h.setSetting("input.path", "/ws/no/vegvesen/admin/subjekt/person/PersonTjeneste/v1")



#
# Pickle stuff, for later (store/retreive)
#

#data1 = {'a': [1, 2.0, 3, 4+6j],
#         'b': ('string', u'Unicode string'),
#         'c': None}

#selfref_list = [1, 2, 3]
#selfref_list.append(selfref_list)

#output = open('data.pkl', 'wb')

# Pickle dictionary using protocol 0.
#pickle.dump(data1, output)

# Pickle the list using the highest protocol available.
#pickle.dump(selfref_list, output, -1)

#output.close()