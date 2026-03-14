from yklibpy.common.util_yaml import UtilYaml
import argparse
from pathlib import Path

def load_yamlx(path: Path) -> dict:
  # Util.xyz()
  assoc = UtilYaml.load_yaml(path)
  # print(f'assoc={assoc}|')
  return assoc

def load_yaml_main() -> dict:
  parser = argparse.ArgumentParser(
      description="Load yaml file, and display YAML."
  )
  parser.add_argument("yamlfile", help="input yaml file")
  args = parser.parse_args()
  args.yamlfile
  yamlfile_path = Path(args.yamlfile)
  assoc = load_yamlx(yamlfile_path)
  # print(f'assoc={assoc}')
  # print('=========')
  return assoc
