from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view
import xml.etree.ElementTree as ET

def parse_evtx(evtx_path):
    """
    Parses an .evtx file and yields log entries.
    Each entry is a dict with 'timestamp', 'message', 'source_file'.
    """
    try:
        with Evtx(evtx_path) as log:
            for record in log.records():
                xml_content = record.xml()
                try:
                    root = ET.fromstring(xml_content)
                    
                    # Namespace handling is tricky in EVTX XML, so we strip namespaces or just look for tags regardless
                    # For simplicity, let's extract the EventID and the raw XML or specific data
                    
                    # Typical structure:
                    # <Event xmlns="...">
                    #   <System>
                    #     <TimeCreated SystemTime="..." />
                    #     ...
                    #   </System>
                    #   <EventData> ... </EventData>
                    # </Event>

                    # Extract Timestamp
                    # Note: XML namespaces in ElementTree require {uri}tag syntax
                    # We'll just define the namespace
                    ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
                    
                    time_created = root.find(".//ns:TimeCreated", ns)
                    timestamp = time_created.get("SystemTime") if time_created is not None else "Unknown"

                    # Extract Message (simplistic: just dump the XML or find EventData)
                    # For a "log recorder", raw XML or a summary is fine.
                    # Let's clean it up slightly to just be the inner text or relevant data
                    message = xml_content # Store full XML to ensure we capture all data changes

                    yield {
                        "timestamp": timestamp,
                        "message": f"RECORD_ID={record.record_num()} " + message.replace("\n", " ").replace("\r", " "),
                        "source_file": evtx_path
                    }

                except Exception as e:
                    yield {
                        "timestamp": "Error",
                        "message": f"Error parsing record: {str(e)}",
                        "source_file": evtx_path
                    }
    except Exception as e:
        print(f"Failed to open EVTX file {evtx_path}: {e}")
        return []
