import xml.etree.cElementTree as ElementTree
import pprint
from collections import OrderedDict

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        childrenNames = [child.tag for child in parent_element.getchildren()]
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))

                if childrenNames.count(element.tag) > 1:
                    try:
                        currentValue = self[element.tag]
                        currentValue.append(aDict)
                        self.update({element.tag: currentValue})
                    except: #the first of its kind, an empty list must be created
                        self.update({element.tag: [aDict]}) #aDict is written in [], i.e. it will be a list
                else:
                    self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})

if __name__ == '__main__':
    tree = ElementTree.parse('opcodes.xml')
    root = tree.getroot()
    xmldict = XmlDictConfig(root)
    maindict = {}
    for element in xmldict['category']:
        second = ""
        if element['name'] == 'Utilities':
            continue
        esplit = element['name'].split(':')
        if len(esplit) > 1:
            first = element['name'].split(':')[0]
            second = element['name'].split(':')[1]
            if not maindict.has_key(first):
                maindict[first] = {}
            write = 1
        else:
            first = element['name']
            write = 0
                   
        opcodes = []
        
        if isinstance(element['opcode'], XmlListConfig):
            for opcode in element['opcode']:
                try:
                    if isinstance(opcode['synopsis'], XmlDictConfig):
                        opcodes.append(opcode['synopsis']['opcodename'])
                    else:
                        for op in opcode['synopsis']:
                            try:
                                if isinstance(op.values()[0], XmlListConfig):
                                    opcodes.extend(list(op.values()[0]))
                                else:
                                    opcodes.append(op.values()[0])
                            except:
                                opcodes.extend(op)
                except:
                    pass
        opcodes = [op for op in opcodes if op != '.']  
        opcodes = list(OrderedDict.fromkeys(opcodes))
         
        if write == 0:
            if first == "Table Control" and second == "":
                if not maindict.has_key(first):
                    maindict[first] = {}
                maindict[first][second] = opcodes
            else:
                maindict[first] = opcodes
        else:
            if maindict[first].has_key(second):
                maindict[first][second].extend(opcodes)
            else:    
                maindict[first][second] = opcodes
                
    pp = pprint.PrettyPrinter()
    str = pp.pformat(maindict)
    with open("opcodestree.py", "w") as f:
        f.write(str)
