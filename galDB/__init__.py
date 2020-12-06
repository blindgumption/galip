"""
an interface to enable the use of different data stores to hold galip's data

GALIP is initially implemented using MongoDB to store geolocation data.
The galDB package is intended to encapsulate how the data is stored and retrieved.
At some pointt, the data could be stored in PostgreSQL or some clould hosted document store, 
  or maybe even something in memory, like Redis.

  It's even conceivable some data could be stored in RAM, and some in slower access memory.
"""


