**Purpose**: Represent processes, consisting of simultaneous and serial subprocesses.  
**Example Use Case**: This example describes a hot rolling process that consists of a number of subprocesses (heating, one rolling pass, cooling) that are proper occurent part of the superordinate hot rolling process. The hot rolling process has distinct first (ro:starts with) and last (ro:ends with) subprocesses and the subprocesses precede each other in the specified order.  
The hot rolling process has a specified input of an ingot which ceases to exist during the process and a specified output of a strand (a very long hot rolled object) which starts to exist during the process.  
Notes: 
- What is not being said but could be expressed in addition: the ingots bfo:history process ends with the hot rolling process while the strands bfo:history starts with the hot rolling process. 
- We have no proper class available for the strand, so we use the next best up the class hierarchy which is bfo:object.

