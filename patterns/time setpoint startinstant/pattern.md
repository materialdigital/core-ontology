**Purpose**: Represent the timepoint a process was started.

The process itself is a complex entity involving participants, changes and time. It's "time aspect" is a one dimensional temporal region, in this case an uninterrupted one, a temporal interval. The interval is bounded by two bfo:temporal instants. The first instant is related by bfo:has first instant, the last is related by bfo:has last instant. 
The position of the first temporal instant with respect to a reference system is quantified using a timepoint, which is a subclass of value specification in combination with the dataproperty time:inXSDDateTimeStamp which implies UTC as reference system. 

There also exists a plan specification and this plan specification has a part which is a 'pmd:specification datum' that 'obi:has value specification' pointing to the timepoint. By this it becomes clear that the timepoint is a setpoint.

Sidenote: The bfo:occupies temporal region relation of the process to the temporal interval is functional, meaning that this is the sole and identity defining temporal interval of the process. 