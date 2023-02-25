from mtkh_modules.mtkh_vars import MTKH_vars as vars

class MTKH_Partition_GPT_vars:
	num_part_entries = 0
	part_entry_size = 0
	part_entry_start_lba = 0

	def __init__(self):
		try:
			if vars.args.gpt_num_part_entries is not None:
				self.num_part_entries = int(vars.args.gpt_num_part_entries)
		except:
			pass
		try:
			if vars.args.gpt_part_entry_size is not None:
				self.part_entry_size = int(vars.args.gpt_part_entry_size)
		except:
			pass
		try:
			if vars.args.gpt_part_entry_start_lba is not None:
				self.part_entry_size = int(vars.args.gpt_part_entry_start_lba)
		except:
			pass
