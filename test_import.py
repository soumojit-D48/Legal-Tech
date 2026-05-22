import sys
sys.path.insert(0, r"c:\Users\subhankar nath\Desktop\Legal-Tech")

import services.ai.schemas.counter_offer as schema_module
import services.ai.app.pipelines.counter_offer as pipeline_module

print(f"Schema module: {schema_module.__file__}")
print(f"Pipeline module: {pipeline_module.__file__}")
