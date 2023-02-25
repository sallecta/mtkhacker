from mtkh_modules.partition.gpt.mtkh_partition_gpt_vars import MTKH_Partition_GPT_vars

class MTKH_Partition_GPT:
	vars = None
	def __init__(self):
		self.vars = MTKH_Partition_GPT_vars()
		
	def daloader_get_gpt(self, parttype=None):
		fpartitions = []
		data, guid_gpt = self.da.partition.get_gpt(self.config.gpt_settings, parttype)
		if guid_gpt is None:
			return [False, fpartitions]
		return [data, guid_gpt]
		
	def get(self, parttype="user"):
		data = self.readflash(addr=0, length=2 * self.config.pagesize, filename="", parttype=parttype, display=False)
		if data[:9] == b"EMMC_BOOT" and self.read_pmt is not None:
			partdata, partentries = self.read_pmt()
			if partdata == b"":
				return None, None
			else:
				return partdata, partentries
		elif data[:8] == b"UFS_BOOT" and self.read_pmt is not None:
			partdata, partentries = self.read_pmt()
			if partdata == b"":
				return None, None
			else:
				return partdata, partentries
		if data == b"":
			return None, None
		guid_gpt = gpt(
			num_part_entries=self.vars.num_part_entries,
			part_entry_size=self.vars.part_entry_size,
			part_entry_start_lba=self.vars.part_entry_start_lba,
		)
		header = guid_gpt.parseheader(data, self.config.pagesize)
		if header.signature == b'\x00\x00\x00\x00\x00\x00\x00\x00':
			data = self.readflash(addr=self.mtk.daloader.daconfig.flashsize-0x4000, length=2 * self.config.pagesize, filename="", parttype=parttype, display=False)
			header = guid_gpt.parseheader(data, self.config.pagesize)
			if header.signature == b'\x00\x00\x00\x00\x00\x00\x00\x00':
				return None, None
		sectors = header.first_usable_lba
		if sectors == 0:
			return None, None
		data = self.readflash(addr=0, length=sectors * self.config.pagesize, filename="",
							  parttype=parttype, display=False)
		if data == b"":
			return None, None
		guid_gpt.parse(data, self.config.pagesize)
		return data, guid_gpt

