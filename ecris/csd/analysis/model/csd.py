from typing import Dict

import numpy as np

class CSD:
    def __init__(self, data: np.ndarray, 
                 timestamp: str,
                 settings: Dict[str, float]) -> None:
        self.data = data
        self.settings = settings
        self.timestamp = timestamp
        self._m_over_q: np.ndarray | None = None

    def save_to_file(self, filename):
        if self._m_over_q is not None:
            data = np.hstack((self._m_over_q, self.data))
            np.savetxt(filename, data, 
                       header='m_over_q,dipole_current,dipole_field,beam_current')
        else:
            raise ValueError('No m_over_q set')

    @property
    def m_over_q(self) -> np.ndarray | None:
        return self._m_over_q

    @m_over_q.setter
    def m_over_q(self, to_set: np.ndarray) -> np.ndarray:
        self._m_over_q = to_set
        return self._m_over_q

    @property
    def time(self) -> np.ndarray:
        return self.data[:,0]

    @property
    def dipole_current(self) -> np.ndarray:
        """Dipole current in micro-amps (A)"""
        return self.data[:,1]*1E6

    @property
    def dipole_field(self) -> np.ndarray:
        """Dipole field in Tesla (T)"""
        return self.data[:,2]

    @property
    def beam_current(self) -> np.ndarray:
        """Beam current in micro amps (A)"""
        return self.data[:,3]*1E6

    @property
    def extraction_voltage(self) -> float:
        """Extraction voltage in kilovolts (kV)"""
        return self.settings['extraction_v']
