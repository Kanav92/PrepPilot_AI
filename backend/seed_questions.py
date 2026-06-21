import sys, os
sys.path.insert(0, ".")
from dotenv import load_dotenv
import psycopg2

load_dotenv()

questions = [
    # DSA
    ("DSA", "easy",   "What is the time complexity of binary search?",
     ["O(log n)", "sorted array", "divide and conquer"]),
    ("DSA", "medium", "Explain how a hash table works and how collisions are handled.",
     ["hash function", "chaining", "open addressing", "load factor"]),
    ("DSA", "medium", "What is the difference between a stack and a queue?",
     ["LIFO", "FIFO", "push/pop", "enqueue/dequeue"]),
    ("DSA", "hard",   "Explain Dijkstra's algorithm and its time complexity.",
     ["greedy", "priority queue", "O((V+E) log V)", "shortest path"]),
    ("DSA", "hard",   "What is dynamic programming? Give an example.",
     ["memoization", "tabulation", "overlapping subproblems", "optimal substructure"]),

    # DBMS
    ("DBMS", "easy",   "What is the difference between SQL and NoSQL databases?",
     ["structured", "schema", "scalability", "ACID"]),
    ("DBMS", "medium", "What is database indexing and why is it used?",
     ["B-tree", "query speed", "write overhead", "primary index"]),
    ("DBMS", "medium", "Explain the ACID properties of a transaction.",
     ["atomicity", "consistency", "isolation", "durability"]),
    ("DBMS", "hard",   "What is database normalization? Explain up to 3NF.",
     ["1NF", "2NF", "3NF", "redundancy", "functional dependency"]),
    ("DBMS", "hard",   "What is a deadlock in databases and how is it handled?",
     ["wait-for graph", "timeout", "deadlock detection", "rollback"]),

    # OS
    ("OS", "easy",   "What is the difference between a process and a thread?",
     ["memory space", "lightweight", "context switching", "PCB"]),
    ("OS", "medium", "What is a deadlock and what are the four necessary conditions?",
     ["mutual exclusion", "hold and wait", "no preemption", "circular wait"]),
    ("OS", "medium", "Explain the concept of virtual memory.",
     ["paging", "page fault", "swap space", "page table"]),
    ("OS", "hard",   "Compare paging and segmentation in memory management.",
     ["fixed size", "variable size", "fragmentation", "page table"]),
    ("OS", "hard",   "What is a semaphore and how does it differ from a mutex?",
     ["counting semaphore", "binary semaphore", "ownership", "signaling"]),

    # CN
    ("CN", "easy",   "What is the OSI model? Name its 7 layers.",
     ["physical", "data link", "network", "transport", "session", "presentation", "application"]),
    ("CN", "medium", "What is the difference between TCP and UDP?",
     ["reliability", "connection-oriented", "latency", "acknowledgment"]),
    ("CN", "medium", "Explain how DNS works.",
     ["resolver", "root server", "authoritative server", "caching", "TTL"]),
    ("CN", "hard",   "What is the TCP three-way handshake?",
     ["SYN", "SYN-ACK", "ACK", "connection establishment"]),
    ("CN", "hard",   "What is HTTP vs HTTPS and how does TLS work?",
     ["encryption", "certificate", "handshake", "symmetric key", "CA"]),

    # OOP
    ("OOP", "easy",   "What are the four pillars of OOP?",
     ["encapsulation", "inheritance", "polymorphism", "abstraction"]),
    ("OOP", "medium", "What is the difference between method overloading and overriding?",
     ["compile time", "runtime", "signature", "inheritance"]),
    ("OOP", "medium", "Explain the SOLID principles.",
     ["single responsibility", "open/closed", "Liskov", "interface segregation", "dependency inversion"]),
    ("OOP", "hard",   "What is the difference between composition and inheritance?",
     ["has-a", "is-a", "tight coupling", "flexibility"]),
    ("OOP", "hard",   "What are design patterns? Explain Singleton and Factory.",
     ["creational", "structural", "behavioral", "instance control", "object creation"]),
]

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.executemany(
    """
    INSERT INTO question_bank (topic, difficulty, question_text, expected_concepts)
    VALUES (%s, %s, %s, %s)
    """,
    questions
)

conn.commit()
cur.execute("SELECT COUNT(*) FROM question_bank")
count = cur.fetchone()[0]
print(f"Seeded {count} questions into question_bank.")
cur.close()
conn.close()
