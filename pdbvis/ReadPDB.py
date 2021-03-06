import re
import sys, os
import bpy

# Read PDB file and get information about the molecule
class PDBReader():
    def __init__(self, path):
        splitPath = re.split(r"/|\\", path)
        self.path = "/".join(splitPath[:-1])
        self.name = splitPath[-1]
        self.atoms = []
        self.bonds = []
        self.text = ""
        self.readFile()
        self.getAtoms()

    def readFile(self):
        """
        Read lines from files if file has a valid PDB extension
        """
        splitName = self.name.split('.')
        if splitName[-1] != 'pdb':
            raise ValueError(f"{self.name} is not a valid PDB file.")
        with open(os.path.join(self.path, self.name), 'r') as f:
            self.text = f.read()
        self.text = self.text.split('\n')
        print(f"{self.name} succesfully loaded!")


    def getAtoms(self):
        """
        Get all atoms from PDB file and read all their properties
        """
        for s in self.text:
            if s[0:5].replace(" ", "") == "ATOM":
                atom = {"atom": s[0:5], "serial": s[6:10], "name": s[12:15], "altLoc": s[16],
                    "resName": s[17:19], "chainID": s[21], "resSeq": s[22:25],
                    "iCode": s[26], "x": s[30:37], "y": s[38:45], "z": s[46:53],
                    "occupancy": s[54:59], "tempFactor": s[60:65], "element": s[66:78],
                    "charge": s[79:80]}
                for info in ["atom", "serial", "name", "altLoc", "resName", "chainID",
                            "resSeq", "iCode", "x", "y", "z", "occupancy", "tempFactor",
                            "element", "charge"]:
                    atom[info] = atom[info].strip()
                try:
                    atom["serial"] = int(atom["serial"]) if atom["serial"] != "" else None
                    atom["x"] = float(atom["x"]); atom["y"] = float(atom["y"])
                    atom["z"] = float(atom["z"]);
                except ValueError:
                    print(atom)
                    print(f"Atom {atom['serial']} serial or 3D position can't be decoded")
                    continue
                try:
                    atom["occupancy"] = float(atom["occupancy"])
                    atom["tempFactor"] = float(atom["tempFactor"])
                    atom["resSeq"] = int(atom["resSeq"])
                except ValueError:
                    pass
                self.atoms.append(atom)



# Convert from PDB to FBX using blender API
class PDBConverter():
    def __init__(self, input, output):
        splitInput = re.split(r"/|\\", input)
        self.inputPath = "/".join(splitInput[:-1]) # input file path
        self.inputName = splitInput[-1] # input file name
        splitOutput = re.split(r"/|\\", output)
        self.outputPath = "/".join(splitOutput[:-1]) # output file path
        self.outputName = splitOutput[-1] # output file name
        self.atomProperties = BlenderPDBInit() # init atom properties with default path
        self.main() # call main method


    def main(self):
        """
        Check paths, init scene and convert file from PDB, lastly export to FBX
        """
        print("Checking paths...")
        self.checkPaths() # check if given paths exist
        print("Initializing blender scene...")
        self.initScene() # start blender scene
        print("Creating model...")
        self.createModel() # Create mesh for each atom
        print("Exporting model...")
        self.exportModel() # export model into FBX file
        print("Everything with PDB generator done!")


    def createModel(self):
        self.readFile()


    def exportModel(self):
        bpy.ops.export_scene.fbx(filepath=os.path.join(self.outputPath, self.outputName))


    def checkPaths(self):
        """
        Check if given path (input and output) are valid ones (.pdb and .fbx)
        """
        splitName = self.inputName.split('.')
        if splitName[-1] != 'pdb' or len(splitName) != 2:
            raise ValueError("Invalid input file given. File must be a valid PDB file")
        splitName = self.outputName.split('.')
        if splitName[-1] != 'fbx' or len(splitName) != 2:
            raise ValueError("Invalid output file given. File must have a FBX extension or delete dots inside it")


    def initScene(self):
        """
        Start blender scene and remove initial setup (cube, camera, light and all objects)
        """
        allObj = bpy.data.objects
        for obj in allObj:
            bpy.data.objects.remove(obj)


    def readFile(self):
        """
        Read PDB file using `PDBReader` and convert into mesh
        """
        reader = PDBReader(os.path.join(self.inputPath, self.inputName))
        for atom in reader.atoms:
            self.addAtom(atom)


    def addAtom(self, atom):
        """
        Add a mesh from given `atom`
        """
        element = atom["element"]
        radius = self.atomProperties.atoms[element]["RadiusUsed"]
        # Create mesh and locate it
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=6, radius=radius, location=(atom["x"], atom["y"], atom["z"]))

        # Select `ob` and make it active
        ob = bpy.context.view_layer.objects.active
        ob.name = f"Atom_{atom['serial']}"

        material = self.elementMaterial(element)

        # Assign material to object
        if ob.data.materials:
            # assign to 1st material slot
            ob.data.materials[0] = material
        else:
            # no slots
            ob.data.materials.append(material)


    def elementMaterial(self, element):
        """
        Check if `element` material was already done, if not create it.
        """
        mat = bpy.data.materials.get(element)
        if not mat:
            # create material
            mat = bpy.data.materials.new(name=element)
            mat.diffuse_color = self.atomProperties.atoms[element]["Color"]
        return mat




class BlenderPDBInit():
    def __init__(self, elementsPropertiesPath=None):
        self.infoPath = "pdbvis/Atom_info.dat" if not elementsPropertiesPath else elementsPropertiesPath
        # Data from each atom to be retrieved, each tuple has the property name
        # (as in file), and the regex way to read the property
        self.data = [
            ("Number", r"\d+"),
            ("Name", r"\w+"),
            ("Short name", r"\w+"),
            ("Color", ",".join([r"\d+[.]\d+"]*4)),
            ("Diffuse intensity", r'\d+[.]\d+'),
            ("Specular intensity", r'\d+[.]\d+'),
            ("Specular hard", r'\d+'),
            ("Traceable", r'\d+'),
            ("Shadow receive", r'\d+'),
            ("Shadow cast", r"\d+"),
            ("Radius used", r"\d+[.]\d+"),
            ("Radius covalent", r"\d+[.]\d+"),
            ("Radius atomic", r"\d+[.]\d+"),
            ("Charge state", r"(-)?\d+([.]\d+)?"),
            ("Radius ionic", r"\d+[.]\d+"),
        ]
        self.atoms = {}
        self.readElementsProperties()


    def readElementsProperties(self):
        """
        Read dat file with all atoms information, split by new line and/or 'Atom' phrase
        """
        info = [] # raw elements info
        with open(self.infoPath) as f:
            info = [item.replace('\n', '') for item in f.read().split('Atom')]

        allMatch = []
        # read all lines and extract data from each element
        for s in info:
            # if line is empty, skip it
            if s.replace(' ', '') == "":
                continue
            matches = self.getMatches(self.data, s)
            # if pattern wasnt succesful, try removing last two items
            if len(matches) == 0:
                matches = self.getMatches(self.data[:-2], s) # skip 'charge' and 'ioinc radius'
                matches[0]["ChargeState"] = None
                matches[0]["RadiusIonic"] = None

            matches = self.transformMatches(matches[0]) # get dictionary from first list item
            allMatch.append(matches) # add this atom results into main matches

        # Create dictionary with all atoms info, keys are atoms symbols (e.g. 'Na')
        self.atoms = {atom["ShortName"]: {key: atom[key] for key in atom.keys() if key != "ShortName"} for atom in allMatch}


    def transformMatches(self, matches, asString=["Name", "ShortName"], asInt=["Number", "ChargeState"]):
        """
        Transform data types for each variable inside matches
        """
        # transform string into numeric data
        for key in matches.keys():
            if key in asString:
                continue
            # colors have four values separated by commas
            if key == "Color":
                nVal = [self.toNumeric(val) for val in matches[key].split(",")]
            # atomic number and charge must be integers
            elif key in asInt:
                nVal = int(matches[key]) if matches[key] else matches[key]
            else:
                pastVal = matches[key]
                nVal = self.toNumeric(matches[key]) if pastVal else pastVal
            matches[key] = nVal # assign new value to dictionary position
        return matches


    def getMatches(self, fields, s):
        """
        Get matches from given fields and string
        """
        pattern = self.createPattern(fields) # create pattern to find
        matches = self.getPatternInString(pattern, s) # get info with pattern
        return matches


    def createPattern(self, fields):
        """
        Create pattern based on all the properties to be readed by given regex
        """
        toCamelCase = lambda name: "".join([word.capitalize() for word in name.replace(',', '').split(" ")])
        patterns = ["\s*:\s*".join([dat[0], "(?P<" + toCamelCase(dat[0]) + ">" + dat[1] + ")"]) for dat in fields]
        pattern = r'{}.*'.format("[\s\S]*" + "\s*".join(patterns))
        return pattern


    def getPatternInString(self, pattern, s):
        """
        Get given dictionary with pattern matches from given string
        """
        compiledPattern = re.compile(pattern)
        matches = [m.groupdict() for m in compiledPattern.finditer(s)]
        return matches


    def toNumeric(self, value):
        """
        Convert string into float value if possible, otherwise return None or raise error
        """
        newVal = None
        try:
            newVal = float(value)
        except ValueError:
            newVal = None
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        return newVal


"""
### Create material
bpy.ops.material.new()
Add a new material

## Add material to mesh
material_index
The face???s material index.
Type  int

## Might work (https://blender.stackexchange.com/questions/23433/how-to-assign-a-new-material-to-an-object-in-the-scene-from-python)
# import bpy

# Select object by name
obj = bpy.data.objects[f"{objName}"]

# Select `obj` and make it active
bpy.context.view_layer.objects.active = obj
obj.select_set(True) # select it

ob = bpy.context.active_object

# Get material
mat = bpy.data.materials.get("Material")
if mat is None:
    # create material
    mat = bpy.data.materials.new(name="Material")
    mat.diffuse_color = [1.0, 1.0, 1.0, 1.0] # base color with 4 float numbers (RGBA color)
    # All material attributes: https://docs.blender.org/api/current/bpy.types.Material.html#bpy.types.Material

# Assign it to object
if ob.data.materials:
    # assign to 1st material slot
    ob.data.materials[0] = mat
else:
    # no slots
    ob.data.materials.append(mat)

#### Export model as FBX
bpy.ops.export_scene.fbx(filepath='')
# Source: https://docs.blender.org/api/current/bpy.ops.export_scene.html?highlight=export#module-bpy.ops.export_scene
"""

# Not working well
"""
def withRERead():
    fields = [r"\s*ATOM", r"(?P<serial>\d+)", r"(?P<name>\w+)", r"(?P<altloc>\w+)?",
            r"(?P<resName>\w+)?", r"(?P<chainID>-?\w+)", r"(?P<resSeq>-?\d+)", r"(?P<iCode>\w+)?",
            r"(?P<x>-?\d+.\d+)", r"(?P<y>-?\d+.\d+)", r"(?P<z>-?\d+.\d+)", r"(?P<occupancy>\d+.\d+)",
            r"(?P<tempFactor>\d+.\d+)", r"(?P<element>\w+)", r"(?P<charge>\w+)?$"]
    pattern = r'{}\s+'.format("\s+".join(fields))
    atomPattern = re.compile(pattern)
    s = "ATOM     32  N  AARG A  -3      11.281  86.699  94.383  0.50 35.88           N"
    [m for m in atomPattern.finditer(s)]
    matches = [m.groupdict() for m in atomPattern.finditer(s)]
    matches
"""
