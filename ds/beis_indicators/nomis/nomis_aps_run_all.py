"""
"""

import os
from beis_indicators import project_dir

print(f"{project_dir}")

print('Collecting raw APS files')

os.system (f"python '{project_dir}/beis_indicators/nomis/aps/nomis_aps.py'")

print('Creating indicator')

os.system (f"python '{project_dir}/beis_indicators/nomis/aps/make_aps_indicators.py'")
