import './style.css'

import { pickAndImport } from './importFile'
import { clearMarkers, enableMarkerCreation, loadMarkers } from './markers'
import { buildToolbar } from './toolbar'

buildToolbar({ onImport: pickAndImport, onClear: () => void clearMarkers() })
enableMarkerCreation()
void loadMarkers()
