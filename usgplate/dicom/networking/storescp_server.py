import logging
from dataclasses import dataclass
from pathlib import Path
from queue import Queue

import pynetdicom
import pynetdicom.sop_class
from pynetdicom._globals import ALL_TRANSFER_SYNTAXES

from usgplate.dicom.entities.dicom_instance_info import DicomInstanceInfo
from ..repository import DCMFileRepository

logger = logging.Logger(__name__)


@dataclass(eq=True)
class StoreSCPConfig:
    dcm_repository_root: str|Path="output"
    ae_title: str="STORE_SCP"
    port: int = 4243


class StoreSCPServer:

    def __init__(self,
                 store_scp_config: StoreSCPConfig,
                 ) -> None:
        self.ae_title = store_scp_config.ae_title
        self.port = store_scp_config.port
        self.dcm_repository_root = Path(store_scp_config.dcm_repository_root)
        self.dcm_repository = DCMFileRepository(self.dcm_repository_root)
        self.transfer_syntaxes = ALL_TRANSFER_SYNTAXES[:]

        self.ae = pynetdicom.AE(ae_title=self.ae_title)
        for context in pynetdicom.AllStoragePresentationContexts:
            self.ae.add_supported_context(context.abstract_syntax, self.transfer_syntaxes)
        self.ae.add_supported_context(pynetdicom.sop_class.Verification)

        logger.info(f"Starting StoreSCP server on port {self.port}")
        self.server = self.ae.start_server(address=('', self.port),
                                           block=False,
                                           evt_handlers=[(pynetdicom.events.EVT_C_STORE, self.on_c_store)])
        # todo add maxsize
        self.received_queue = Queue()
        

    def on_c_store(self, event: pynetdicom.events.Event):
        logger.debug("Received C-STORE request")
        dataset = event.dataset
        # Maybe could be done better:
        # From documetation on another possibility:
        # Encode the File Meta Information in a new file and append the encoded Data Set to it.
        # This skips having to decode/re-encode the Data Set as in the previous example.
        dataset.file_meta = event.file_meta
        instance_info = DicomInstanceInfo.from_dataset(dataset)
        self.dcm_repository.save(dataset)
        self.received_queue.put(instance_info)
        return 0x0000
    
    def stop(self):
        self.server.shutdown()
        self.server.server_close()
    
    # def __del__(self):
    #     self.stop()
    

    
    


