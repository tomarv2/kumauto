import yaml
import os
from pykwalify.core import Core


c = Core(source_file="demo-transform.yaml", schema_files=["rules-schema.yaml"])
print(c.validate(raise_exception=True))
