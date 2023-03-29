from clint.textui import progress
import requests
import zipfile
import shutil
import os
import subprocess
import json
import codecs
from pathlib import Path

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

def launch_forge_installer(tmp_path: Path):
	p = subprocess.Popen(["java", "-jar", f"{(tmp_path / 'Modpack' / 'forge-1.12.2-14.23.5.2860-installer.jar').absolute()}"])
	p.wait()

def update_launcher_profiles(game_path: Path):
	profile_json_path = game_path / "launcher_profiles.json"
	with codecs.open(profile_json_path, 'r+', encoding='utf-8') as stream:
		data = json.load(stream)
		data['profiles']['MPAP'] = {
			"icon" : "data:image/png;base64,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",
			"gameDir" : f"{(game_path / 'profiles' / 'MPAP').absolute()}",
			"javaArgs" : "-Xms2G -Xmx4G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M",
			"lastVersionId" : "1.12.2-forge-14.23.5.2860",
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
	url = "https://drive.google.com/u/1/uc?id=18osknPnmXpP57R7XPjtsF-YznfXdauSr&export=download&confirm=t"
	tmp_path = Path("./tmp")
	if not os.path.exists(tmp_path):
		os.mkdir(tmp_path)
	file_name = tmp_path / "modpack.zip"
	download_modpack(url, file_name)
	extract_modpack(tmp_path, file_name)
	launch_forge_installer(tmp_path)
	minecraft_path = Path(os.path.expandvars("%appdata%/.minecraft"))
	update_launcher_profiles(minecraft_path)
	copy_mods(tmp_path / "Modpack", minecraft_path)
	shutil.rmtree(tmp_path)
	

if __name__ == '__main__':
	main()