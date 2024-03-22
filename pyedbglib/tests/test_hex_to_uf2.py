"""
Tests covering the hex_to_uf2 module in util
"""

import unittest
import tempfile
from pathlib import Path

from pyedbglib.util.hex_to_uf2 import hex_to_uf2

DATA_FOLDER = Path(__file__).parent.absolute() / 'data'

class TestHexToUf2(unittest.TestCase):
    """Tests for hexfile to UF2 file conversion utility"""

    def _convert_hex_to_uf2_and_check(self, hexfile_path, reference_uf2file_path):
        """Convert hexfile to UF2 file and verify against reference file

        :param hexfile_path: Path to input hex file
        :type hexfile: class:'pathlib.Path'
        :param reference_uf2file_path: Path to reference UF2 file
        :type uf2file: class:'pathlib.Path'
        """
        with tempfile.TemporaryDirectory() as tempdir:
            outputfile_path = Path(tempdir) / 'generated.uf2'

            hex_to_uf2(hexfile_path, outputfile_path)

            with reference_uf2file_path.open('rb') as reference_file:
                with outputfile_path.open('rb') as output_file:
                    reference = reference_file.read()
                    output = output_file.read()
                    self.assertEqual(output,
                                     reference,
                                     msg="UF2 mismatch, {} vs {}".format(outputfile_path, reference_uf2file_path))


    def test_hex_to_uf2(self):
        """
        Test hex to UF2 file conversion using golden sample files
        """
        self._convert_hex_to_uf2_and_check(DATA_FOLDER/'atmega4809_flash_gaps_fuses_lockbits.hex',
                                           DATA_FOLDER/'atmega4809_flash_gaps_fuses_lockbits.uf2')
        self._convert_hex_to_uf2_and_check(DATA_FOLDER/'pic16_flash_eeprom_config.hex',
                                           DATA_FOLDER/'pic16_flash_eeprom_config.uf2')
