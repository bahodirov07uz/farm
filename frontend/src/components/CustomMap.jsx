// frontend/src/components/CustomMap.jsx
import { useState, useEffect, useRef } from 'react';
import { MapPin, Navigation, ArrowRight, Plus, Minus, Maximize2 } from 'lucide-react';

const CustomMap = ({ 
  userLocation, 
  branches = [], 
  selectedBranch = null,
  onBranchSelect,
  showRoute = false,
  className = ""
}) => {
  const canvasRef = useRef(null);
  const [hoveredBranch, setHoveredBranch] = useState(null);
  const [zoom, setZoom] = useState(13);
  const [center, setCenter] = useState({
    lat: userLocation?.latitude || 41.2995,
    lng: userLocation?.longitude || 69.2401
  });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [tiles, setTiles] = useState({});
  const [tileCache, setTileCache] = useState({});

  useEffect(() => {
    if (userLocation) {
      setCenter({
        lat: userLocation.latitude,
        lng: userLocation.longitude
      });
    }
  }, [userLocation]);

  // Convert lat/lng to pixel coordinates
  const latLngToPixel = (lat, lng, zoom, canvasWidth, canvasHeight) => {
    const scale = (1 << zoom) * 256;
    const worldX = (lng + 180) / 360 * scale;
    const worldY = (1 - Math.log(Math.tan(lat * Math.PI / 180) + 1 / Math.cos(lat * Math.PI / 180)) / Math.PI) / 2 * scale;
    
    const centerWorldX = (center.lng + 180) / 360 * scale;
    const centerWorldY = (1 - Math.log(Math.tan(center.lat * Math.PI / 180) + 1 / Math.cos(center.lat * Math.PI / 180)) / Math.PI) / 2 * scale;
    
    const x = canvasWidth / 2 + (worldX - centerWorldX);
    const y = canvasHeight / 2 + (worldY - centerWorldY);
    
    return { x, y };
  };

  // Convert pixel to lat/lng
  const pixelToLatLng = (x, y, zoom, canvasWidth, canvasHeight) => {
    const scale = (1 << zoom) * 256;
    
    const centerWorldX = (center.lng + 180) / 360 * scale;
    const centerWorldY = (1 - Math.log(Math.tan(center.lat * Math.PI / 180) + 1 / Math.cos(center.lat * Math.PI / 180)) / Math.PI) / 2 * scale;
    
    const worldX = centerWorldX + (x - canvasWidth / 2);
    const worldY = centerWorldY + (y - canvasHeight / 2);
    
    const lng = worldX / scale * 360 - 180;
    const latRad = Math.atan(Math.sinh(Math.PI * (1 - 2 * worldY / scale)));
    const lat = latRad * 180 / Math.PI;
    
    return { lat, lng };
  };

  // Get tile coordinates for a given lat/lng/zoom
  const getTileCoordinates = (lat, lng, zoom) => {
    const scale = 1 << zoom;
    const x = Math.floor((lng + 180) / 360 * scale);
    const y = Math.floor((1 - Math.log(Math.tan(lat * Math.PI / 180) + 1 / Math.cos(lat * Math.PI / 180)) / Math.PI) / 2 * scale);
    return { x, y, zoom };
  };

  // Load map tiles
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    
    // Set canvas size for retina displays
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const width = rect.width;
    const height = rect.height;

    // Clear canvas with background color
    ctx.fillStyle = '#e5e7eb';
    ctx.fillRect(0, 0, width, height);

    // Calculate which tiles we need
    const tileCoord = getTileCoordinates(center.lat, center.lng, zoom);
    const numTilesX = Math.ceil(width / 256) + 2;
    const numTilesY = Math.ceil(height / 256) + 2;
    
    const startTileX = tileCoord.x - Math.floor(numTilesX / 2);
    const startTileY = tileCoord.y - Math.floor(numTilesY / 2);

    // Draw tiles
    const tilesToLoad = [];
    for (let i = 0; i < numTilesX; i++) {
      for (let j = 0; j < numTilesY; j++) {
        const tx = startTileX + i;
        const ty = startTileY + j;
        const tileKey = `${zoom}/${tx}/${ty}`;
        
        // Calculate tile position on canvas
        const centerPixel = latLngToPixel(center.lat, center.lng, zoom, width, height);
        const tileLatLng = tileToLatLng(tx, ty, zoom);
        const tilePixel = latLngToPixel(tileLatLng.lat, tileLatLng.lng, zoom, width, height);
        
        const tileX = tilePixel.x;
        const tileY = tilePixel.y;

        // Draw tile if cached
        if (tileCache[tileKey]) {
          ctx.drawImage(tileCache[tileKey], tileX, tileY, 256, 256);
        } else {
          // Draw placeholder
          ctx.fillStyle = '#f3f4f6';
          ctx.fillRect(tileX, tileY, 256, 256);
          ctx.strokeStyle = '#d1d5db';
          ctx.strokeRect(tileX, tileY, 256, 256);
          
          tilesToLoad.push({ tx, ty, tileKey, tileX, tileY });
        }
      }
    }

    // Load missing tiles
    tilesToLoad.forEach(({ tx, ty, tileKey }) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      // Using OpenStreetMap tiles
      img.src = `https://tile.openstreetmap.org/${zoom}/${tx}/${ty}.png`;
      
      img.onload = () => {
        setTileCache(prev => ({ ...prev, [tileKey]: img }));
      };
    });

    // Draw route if needed
    if (showRoute && userLocation && selectedBranch) {
      const userPos = latLngToPixel(userLocation.latitude, userLocation.longitude, zoom, width, height);
      const branchPos = latLngToPixel(
        parseFloat(selectedBranch.latitude),
        parseFloat(selectedBranch.longitude),
        zoom,
        width,
        height
      );

      // Draw route line
      ctx.strokeStyle = '#6366f1';
      ctx.lineWidth = 4;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.shadowColor = 'rgba(99, 102, 241, 0.5)';
      ctx.shadowBlur = 10;
      
      ctx.beginPath();
      ctx.moveTo(userPos.x, userPos.y);
      
      // Create a curved path
      const midX = (userPos.x + branchPos.x) / 2;
      const midY = (userPos.y + branchPos.y) / 2;
      const controlX = midX + (userPos.y - branchPos.y) * 0.2;
      const controlY = midY - (userPos.x - branchPos.x) * 0.2;
      
      ctx.quadraticCurveTo(controlX, controlY, branchPos.x, branchPos.y);
      ctx.stroke();
      
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
    }

    // Draw user location
    if (userLocation) {
      const pos = latLngToPixel(userLocation.latitude, userLocation.longitude, zoom, width, height);

      // Outer pulsing circle
      const pulse = Math.sin(Date.now() / 500) * 5 + 20;
      ctx.fillStyle = 'rgba(59, 130, 246, 0.15)';
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, pulse, 0, Math.PI * 2);
      ctx.fill();

      // Middle circle
      ctx.fillStyle = 'rgba(59, 130, 246, 0.4)';
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 12, 0, Math.PI * 2);
      ctx.fill();

      // Inner circle
      ctx.fillStyle = '#3b82f6';
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 8, 0, Math.PI * 2);
      ctx.fill();

      // White center dot
      ctx.fillStyle = 'white';
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 3, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw branches
    branches.forEach((branch) => {
      if (!branch.latitude || !branch.longitude) return;

      const pos = latLngToPixel(
        parseFloat(branch.latitude),
        parseFloat(branch.longitude),
        zoom,
        width,
        height
      );

      const isHovered = hoveredBranch?.id === branch.id;
      const isSelected = selectedBranch?.id === branch.id;

      // Pin shadow
      ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
      ctx.shadowBlur = 8;
      ctx.shadowOffsetY = 4;

      // Pin shape
      ctx.fillStyle = isSelected ? '#ef4444' : isHovered ? '#fb923c' : '#f59e0b';
      
      ctx.beginPath();
      // Pin body (circle)
      ctx.arc(pos.x, pos.y - 15, 12, 0, Math.PI * 2);
      ctx.fill();
      
      // Pin point (triangle)
      ctx.beginPath();
      ctx.moveTo(pos.x - 6, pos.y - 5);
      ctx.lineTo(pos.x + 6, pos.y - 5);
      ctx.lineTo(pos.x, pos.y + 5);
      ctx.closePath();
      ctx.fill();

      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
      ctx.shadowOffsetY = 0;

      // White ring
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y - 15, 12, 0, Math.PI * 2);
      ctx.stroke();

      // Inner dot
      ctx.fillStyle = 'white';
      ctx.beginPath();
      ctx.arc(pos.x, pos.y - 15, 4, 0, Math.PI * 2);
      ctx.fill();

      // Highlight ring if selected/hovered
      if (isHovered || isSelected) {
        ctx.strokeStyle = isSelected ? '#ef4444' : '#fb923c';
        ctx.lineWidth = 3;
        ctx.globalAlpha = 0.4;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y - 15, 18, 0, Math.PI * 2);
        ctx.stroke();
        ctx.globalAlpha = 1;
      }
    });

    // Animation loop for pulsing user location
    const animationFrame = requestAnimationFrame(() => {
      if (canvasRef.current) {
        const event = new CustomEvent('redraw');
        window.dispatchEvent(event);
      }
    });
    
    return () => cancelAnimationFrame(animationFrame);
  }, [center, zoom, branches, userLocation, selectedBranch, showRoute, hoveredBranch, tileCache]);

  const tileToLatLng = (x, y, zoom) => {
    const n = Math.pow(2, zoom);
    const lng = x / n * 360 - 180;
    const lat = Math.atan(Math.sinh(Math.PI * (1 - 2 * y / n))) * 180 / Math.PI;
    return { lat, lng };
  };

  // Handle mouse interactions
  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({
      x: e.clientX,
      y: e.clientY,
      centerLat: center.lat,
      centerLng: center.lng
    });
  };

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (isDragging) {
      const dx = e.clientX - dragStart.x;
      const dy = e.clientY - dragStart.y;
      
      const scale = (1 << zoom) * 256;
      const metersPerPixel = 156543.03392 * Math.cos(center.lat * Math.PI / 180) / scale;
      
      const newLat = dragStart.centerLat - (dy * metersPerPixel / 111320);
      const newLng = dragStart.centerLng - (dx * metersPerPixel / (111320 * Math.cos(center.lat * Math.PI / 180)));
      
      setCenter({ lat: newLat, lng: newLng });
      return;
    }

    // Check if hovering over a branch
    let found = null;
    branches.forEach((branch) => {
      if (!branch.latitude || !branch.longitude) return;

      const pos = latLngToPixel(
        parseFloat(branch.latitude),
        parseFloat(branch.longitude),
        zoom,
        rect.width,
        rect.height
      );

      const dx = x - pos.x;
      const dy = y - (pos.y - 15);
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 15) {
        found = branch;
      }
    });

    setHoveredBranch(found);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleClick = () => {
    if (hoveredBranch && onBranchSelect) {
      onBranchSelect(hoveredBranch);
    }
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -1 : 1;
    setZoom(prev => Math.max(10, Math.min(18, prev + delta)));
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(18, prev + 1));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(10, prev - 1));
  };

  const handleResetView = () => {
    if (userLocation) {
      setCenter({
        lat: userLocation.latitude,
        lng: userLocation.longitude
      });
      setZoom(13);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <canvas
        ref={canvasRef}
        className={`w-full h-full ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={handleClick}
        onWheel={handleWheel}
      />

      {/* Hovered branch info */}
      {hoveredBranch && !selectedBranch && (
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3 max-w-xs pointer-events-none">
          <div className="flex items-start gap-2">
            <MapPin className="w-4 h-4 text-orange-500 mt-1 flex-shrink-0" />
            <div>
              <p className="font-semibold text-sm">{hoveredBranch.name}</p>
              {hoveredBranch.address && (
                <p className="text-xs text-gray-600 mt-1">{hoveredBranch.address}</p>
              )}
              {hoveredBranch.phone && (
                <p className="text-xs text-gray-500 mt-1">{hoveredBranch.phone}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Selected branch with route info */}
      {showRoute && selectedBranch && (
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 pointer-events-none">
          <div className="flex items-center gap-2 mb-2">
            <Navigation className="w-4 h-4 text-blue-600" />
            <span className="font-semibold text-sm">Marshrut</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
            <ArrowRight className="w-4 h-4 text-gray-400" />
            <div className="w-2 h-2 rounded-full bg-red-500"></div>
            <span className="text-gray-600 ml-2">{selectedBranch.name}</span>
          </div>
        </div>
      )}

      {/* Map controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2">
        <button
          onClick={handleZoomIn}
          className="bg-white rounded-lg shadow-lg p-2 hover:bg-gray-50 transition-colors"
          title="Kattalashtirish"
        >
          <Plus className="w-5 h-5" />
        </button>
        <button
          onClick={handleZoomOut}
          className="bg-white rounded-lg shadow-lg p-2 hover:bg-gray-50 transition-colors"
          title="Kichiklashtirish"
        >
          <Minus className="w-5 h-5" />
        </button>
        <button
          onClick={handleResetView}
          className="bg-white rounded-lg shadow-lg p-2 hover:bg-gray-50 transition-colors"
          title="Joylashuvimga qaytish"
        >
          <Navigation className="w-5 h-5" />
        </button>
      </div>

      {/* Attribution */}
      <div className="absolute bottom-2 left-2 bg-white bg-opacity-75 px-2 py-1 rounded text-xs text-gray-600">
        © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer" className="underline">OpenStreetMap</a>
      </div>
    </div>
  );
};

export default CustomMap;