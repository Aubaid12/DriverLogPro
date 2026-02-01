import React, { useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default icon
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

function ChangeView({ bounds }) {
    const map = useMap();
    useEffect(() => {
        if (bounds) {
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [bounds, map]);
    return null;
}

const MapDisplay = ({ routeGeometry }) => {
    let bounds = null;
    if (routeGeometry) {
        // Create a temporary GeoJSON layer to calculate bounds
        const layer = L.geoJSON(routeGeometry);
        bounds = layer.getBounds();
    }

    return (
        <MapContainer center={[39.8283, -98.5795]} zoom={4} style={{ height: '100%', width: '100%' }}>
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            />
            {routeGeometry && (
                <>
                    <GeoJSON data={routeGeometry} style={{ color: '#38bdf8', weight: 4 }} />
                    <ChangeView bounds={bounds} />

                    {/* Render Markers from Route Features */}
                    {routeGeometry.features.map((feature, idx) => {
                        if (!feature.geometry || feature.geometry.type !== "LineString") return null;
                        const coords = feature.geometry.coordinates;
                        if (!coords || coords.length === 0) return null;

                        // OSRM/GeoJSON is [lon, lat], Leaflet needs [lat, lon]
                        const startPt = [coords[0][1], coords[0][0]];
                        const endPt = [coords[coords.length - 1][1], coords[coords.length - 1][0]];

                        // Logic to label markers appropriately
                        // Feature 0: Start -> Pickup
                        // Feature 1: Pickup -> Dropoff

                        const markers = [];

                        if (idx === 0) {
                            markers.push(
                                <Marker position={startPt} key={`start-${idx}`}>
                                    <Popup>Start Location</Popup>
                                </Marker>
                            );
                            markers.push(
                                <Marker position={endPt} key={`pickup-${idx}`}>
                                    <Popup>Pickup Location</Popup>
                                </Marker>
                            );
                        } else {
                            // Subsequent features (Feature 1 is Load leg). 
                            // Its start is same as previous end (Pickup), so skip start.
                            // Just render end (Dropoff)
                            markers.push(
                                <Marker position={endPt} key={`dropoff-${idx}`}>
                                    <Popup>Dropoff Location</Popup>
                                </Marker>
                            );
                        }

                        return markers;
                    })}
                </>
            )}
        </MapContainer>
    );
};

export default MapDisplay;
