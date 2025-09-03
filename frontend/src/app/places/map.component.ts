import {
  Component, ElementRef, EventEmitter, Input, OnChanges, OnDestroy,
  AfterViewInit, Output, SimpleChanges, ViewChild
} from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  selector: 'app-map',
  imports: [CommonModule],
  template: `<div #el class="map"></div>`,
  styles: [`.map{width:100%;height:280px;border-radius:12px;border:1px solid #eee;background:#f5f5f5}`]
})
export class MapComponent implements AfterViewInit, OnChanges, OnDestroy {
  @ViewChild('el', { static: false }) el!: ElementRef<HTMLDivElement>;
  @Input() lat = 0;
  @Input() lon = 0;
  @Output() latLonChange = new EventEmitter<{ lat: number; lon: number }>();

  private L: typeof import('leaflet') | null = null;
  private map?: import('leaflet').Map;
  private marker?: import('leaflet').Marker;

  private get isBrowser() { return typeof window !== 'undefined' && typeof document !== 'undefined'; }

  async ngAfterViewInit(): Promise<void> {
    const rect = this.el.nativeElement.getBoundingClientRect();
    console.log('[Map] rect before init', rect);

    if (!this.isBrowser) return;

    this.L = await import('leaflet');

    const defaultIcon = this.L.icon({
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
    });
    (this.L as any).Marker.prototype.options.icon = defaultIcon;

    const center: [number, number] = [this.lat || 0, this.lon || 0];
    this.map = this.L.map(this.el.nativeElement, { center, zoom: 12, zoomControl: true });

    this.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      detectRetina: true,
      maxZoom: 20,
    }).addTo(this.map);

    this.marker = this.L.marker(center, { draggable: false }).addTo(this.map);

    this.map.on('click', (e: any) => {
      const { lat, lng } = e.latlng;
      this.marker!.setLatLng([lat, lng]);
      this.latLonChange.emit({ lat, lon: lng });
    });

    setTimeout(() => this.map && this.map.invalidateSize(), 0);
    window.addEventListener('resize', this.invalidate, { passive: true });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!this.map || !this.marker) return;
    if (changes['lat'] || changes['lon']) {
      const lat = this.lat || 0;
      const lon = this.lon || 0;
      this.map.setView([lat, lon]);
      this.marker.setLatLng([lat, lon]);
      setTimeout(() => this.map && this.map.invalidateSize(), 0);
    }
  }

  private invalidate = () => { this.map && this.map.invalidateSize(); };

  ngOnDestroy(): void {
    if (this.isBrowser) window.removeEventListener('resize', this.invalidate as any);
    this.map?.remove();
    this.map = undefined;
  }
}
