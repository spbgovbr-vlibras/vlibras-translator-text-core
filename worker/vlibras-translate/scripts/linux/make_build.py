# Create a directory 'build' with the source code and data
import compileall,  os, shutil, glob

path_installation = "/".join(os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-2])
path_source = os.path.join(path_installation, "src")
path_data = os.path.join(path_installation, "data")
path_build = os.path.join(path_installation, "build")

if os.path.exists(path_build):
	shutil.rmtree(path_build)
os.makedirs(path_build)

compileall.compile_dir(path_source, force=True)
files = glob.iglob(os.path.join(path_source, "*.pyc"))
for file in files:
	shutil.move(file, path_build)
shutil.copytree(path_data, path_build+"/data")
os.remove(path_build+"/TranslationServer.pyc")