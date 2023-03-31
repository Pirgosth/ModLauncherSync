from clint.textui import progress
import requests
import zipfile
import shutil
import os
import subprocess
import json
import codecs
from pathlib import Path
from dotenv import load_dotenv
import sys

class InstallerConfig:

	def __init__(self) -> None:
		self.minecraft_path: str = os.getenv("MINECRAFT_PATH")
		self.profile_image: str = os.getenv("PROFILE_IMAGE_BASE64")
		self.forge_version: str = os.getenv("FORGE_VERSION")
		self.forge_jar_file: str = os.getenv("FORGE_JAR_FILE")
		self.modpack_drive_uri: str = os.getenv("MODPACK_DRIVE_URI")


def download_modpack(url, file_name):
	r = requests.get(url, allow_redirects=True, stream=True)
	with open(file_name, 'wb') as file:
		total_length = int(r.headers.get('content-length'))
		for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
			if chunk:
				file.write(chunk)
				file.flush()

def extract_modpack(tmp_path: Path, file_name: Path):
	with zipfile.ZipFile(file_name, 'r') as zip_ref:
		zip_ref.extractall(tmp_path)

def launch_forge_installer(tmp_path: Path, config: InstallerConfig):
	p = subprocess.Popen(["java", "-jar", f"{(tmp_path / 'Modpack' / config.forge_jar_file).absolute()}"])
	p.wait()

def update_launcher_profiles(game_path: Path, config: InstallerConfig):
	profile_json_path = game_path / "launcher_profiles.json"
	with codecs.open(profile_json_path, 'r+', encoding='utf-8') as stream:
		data = json.load(stream)
		data['profiles']['MPAP'] = {
			"icon" : f"data:image/png;base64,{config.profile_image}",
			"gameDir" : f"{(game_path / 'profiles' / 'MPAP').absolute()}",
			"javaArgs" : "-Xms2G -Xmx4G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M",
			"lastVersionId" : config.forge_version,
			"name" : "MPAP",
			"type" : "custom"
		}
		stream.seek(0)
		json.dump(data, stream, indent=2)
		stream.truncate()
		
def copy_mods(modpack_path: Path, game_path: Path):
	dist_mods_folder = game_path / "profiles" / "MPAP" / "mods"
	os.makedirs(dist_mods_folder, exist_ok=True)
	shutil.rmtree(dist_mods_folder)
	shutil.copytree(modpack_path / "mods", dist_mods_folder)


def main():
	load_dotenv(Path(os.path.abspath(sys.argv[0])).parent / ".env")
	config = InstallerConfig()
	url = config.modpack_drive_uri
	tmp_path = Path("./tmp")
	if not os.path.exists(tmp_path):
		os.mkdir(tmp_path)
	file_name = tmp_path / "modpack.zip"
	download_modpack(url, file_name)
	extract_modpack(tmp_path, file_name)
	launch_forge_installer(tmp_path, config)
	minecraft_path = Path(os.path.expandvars(config.minecraft_path))
	update_launcher_profiles(minecraft_path, config)
	copy_mods(tmp_path / "Modpack", minecraft_path)
	shutil.rmtree(tmp_path)
	

if __name__ == '__main__':
	main()