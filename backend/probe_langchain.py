
import sys
import pkg_resources

print("Python executable:", sys.executable)
print("Path:", sys.path)

try:
    import langchain
    print("langchain version:", langchain.__version__)
except ImportError as e:
    print("langchain import failed:", e)

try:
    from langchain.memory import ConversationBufferMemory
    print("Successfully imported ConversationBufferMemory from langchain.memory")
except ImportError as e:
    print("Failed to import from langchain.memory:", e)

try:
    from langchain_core.memory import BaseMemory
    print("Successfully imported BaseMemory from langchain_core.memory")
except ImportError as e:
    print("Failed to import from langchain_core.memory:", e)

# List installed packages matching langchain
for dist in pkg_resources.working_set:
    if "langchain" in dist.project_name.lower():
        print(f"Installed: {dist.project_name}=={dist.version}")
