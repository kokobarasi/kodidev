"""
    Downloaded from http://xbmc-addons.googlecode.com/svn/addons/ 
    this is a modded version of the original addons.xml generator 
    put this version in the root folder of your repo and it will 
    zip up all add-on folders, create a new zip in your zips folder
    and then update the md5 and addons.xml file
    Recoded in python 2 by whufclee (info@totalrevolution.tv) 
"""

import re
import os
import shutil
from hashlib import md5
import zipfile


class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.     
    """

    def __init__(self):
        """Initialising Generator class attributes and create zips root folder."""

        if not os.path.exists('zips'):
            os.makedirs('zips')

        self._remove_binaries()   
        self._generate_addons_file()
        self._generate_md5_file()
        
        print(f'Finished updating addons xml and md5 files.')

    def Create_Zips(self,addon_id,version):
        """Copy over icon, fanart and addon.xml into root zips directory."""
        
        xml_path     = os.path.join(addon_id,'addon.xml')
        addon_folder = os.path.join('zips',addon_id)

        if not os.path.exists(addon_folder): 
            os.makedirs(addon_folder)

        final_zip = os.path.join('zips',addon_id,'{}-{}.zip'.format(addon_id,version))

        if not os.path.exists(final_zip):
            print(f'NEW ADD-ON - Creating zip for: {addon_id} v.{version}')

            zip = zipfile.ZipFile(final_zip, 'w', compression=zipfile.ZIP_DEFLATED )

            root_len = len(os.path.dirname(os.path.abspath(addon_id)))

            for root, dirs, files in os.walk(addon_id):
                archive_root = os.path.abspath(root)[root_len:]

                for f in files:
                        fullpath = os.path.join( root, f )
                        archive_name = os.path.join( archive_root, f )
                        zip.write( fullpath, archive_name, zipfile.ZIP_DEFLATED )
            zip.close()
            

            copyfiles = ['icon.png','fanart.jpg','addon.xml']
            files = os.listdir(addon_id)
            for file in files:
                if file in copyfiles:
                    shutil.copy(os.path.join(addon_id,file),addon_folder)


    def _remove_binaries(self):
        """Remove instances of pyc or pyo binaries from files."""
        
        for parent, dirnames, filenames in os.walk('.'):
            for fn in filenames:
                if fn.lower().endswith('pyo') or fn.lower().endswith('pyc'):
                    compiled = os.path.join(parent, fn)
                    py_file  = compiled.replace('.pyo','.py').replace('.pyc','.py')
                    if os.path.exists(py_file):
                        try:
                            os.remove(compiled)
                            print(f"Removed compiled python file:")
                            print(compiled)
                            print(f'-----------------------------')
                        except:
                            print(f"Failed to remove compiled python file:")
                            print(compiled)
                            print(f'-----------------------------')
                    else:
                        print(f"Compiled python file found but no matching .py file exists:")
                        print(compiled)
                        print(f'-----------------------------')


    def _generate_addons_file(self):
        """Creat zip files in root folder."""

        addons = os.listdir('.')

        addons_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"

        for addon in addons:
            try:
                if not os.path.isdir(addon) or addon == "zips" or addon.startswith('.'):
                    continue
                _path = os.path.join( addon, "addon.xml" )
                xml_lines = open( _path, "r" ).read().splitlines()
                addon_xml = ""

                ver_found = False
                for line in xml_lines:
                    if line.find("<?xml") >= 0:
                        continue
                    if 'version="' in line and not ver_found:
                        version = re.compile('version="(.+?)"').findall(line)[0]
                        ver_found = True
                    addon_xml += line.rstrip() + "\n"

                addons_xml += addon_xml.rstrip() + "\n\n"
                
                self.Create_Zips(addon,version)

            except Exception as e:
                print(f"Excluding {_path} for {e}")


        addons_xml = addons_xml.strip() + "\n</addons>\n"
        self._save_file(addons_xml.encode(), file=os.path.join('zips','addons.xml'))


    def _generate_md5_file(self):
        """Create md5 file in root folder."""
        
        try:
            
            content = open(os.path.join('zips','addons.xml')).read().encode()
            m = md5(content).hexdigest() 
            self._save_file(m, file=os.path.join('zips','addons.xml.md5'))
            
        except Exception as e:
            print(f"An error occurred creating addons.xml.md5 file!\n{e}")

    def _save_file(self,data,file):

        if isinstance(data, bytes):

            try:
                
                open(file, 'w').write(data.decode())
                
            except Exception as e:
                print(f"An error occurred saving {file} file!\n{e}")

        else:
            open(file, 'w').write(data)

if ( __name__ == "__main__" ):
    Generator()
    

