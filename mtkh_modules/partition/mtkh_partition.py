from mtkh_modules.mtkh_vars import MTKH_vars as vars
from mtkh_modules.partition.gpt.mtkh_partition_gpt import MTKH_Partition_GPT

class MTKH_Partition:
	
	gpt = None
	
	def __init__(self):
		if vars.partition is None:
			self.gpt = MTKH_Partition_GPT()
			vars.partition = self
