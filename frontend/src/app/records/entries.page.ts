import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { RecordsService } from './records.service';
import { TravelRecordRead, DestinationType, TravelRecordCreate } from '../models';
import { PlacesService } from '../places/places.service';
import { MapComponent } from '../places/map.component';

@Component({
  standalone: true,
  selector: 'app-entries',
  imports: [CommonModule, ReactiveFormsModule, MapComponent],
  templateUrl: './entries.page.html',
  styleUrls: ['./entries.page.css']
})
export class EntriesPage {
  private fb = inject(FormBuilder);
  private api = inject(RecordsService);
  private places = inject(PlacesService);

  items = signal<TravelRecordRead[]>([]);
  total = signal(0);
  editingId = signal<number | null>(null);
  loading = signal(false);

  // Autocomplete UI state
  query = signal('');
  suggestions = signal<{ place_id: string; description: string }[]>([]);
  showSug = signal(false);

  // Map marker state
  mapLat = signal(0);
  mapLon = signal(0);

  onMapLatLonChange(e: { lat: number; lon: number }) {
  this.mapLat.set(e.lat);
  this.mapLon.set(e.lon);
  this.form.patchValue({ latitude: e.lat, longitude: e.lon });
}

  form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.maxLength(140)]],
    notes: [''],
    country_code: ['US', [Validators.required, Validators.pattern(/^[A-Z]{2}$/)]],
    city: [''],
    latitude: [0, [Validators.required, Validators.min(-90), Validators.max(90)]],
    longitude: [0, [Validators.required, Validators.min(-180), Validators.max(180)]],
    destination_type: 'CITY' as DestinationType, // keep uppercase to match backend enum
    rating: [5, [Validators.required, Validators.min(1), Validators.max(5)]],
    visited_at: [new Date().toISOString(), [Validators.required]],
    place_external_id: [''],
  });

  ngOnInit() { this.refresh(); }

  refresh() {
    this.loading.set(true);
    this.api.list({ limit: 50, offset: 0, order_by: 'visited_at:desc' })
      .subscribe(res => {
        this.items.set(res.items);
        this.total.set(res.total);
        this.loading.set(false);
      });
  }

  // ---------- Google Places integration ----------
  onSearchChange(val: string) {
    this.query.set(val);
    if (!val || val.length < 2) {
      this.suggestions.set([]);
      this.showSug.set(false);
      return;
    }
    this.places.autocomplete(val).subscribe(list => {
      this.suggestions.set(list);
      this.showSug.set(true);
    });
  }

  pickSuggestion(p: { place_id: string; description: string }) {
    this.showSug.set(false);
    this.query.set(p.description);
    this.places.details(p.place_id).subscribe(d => {
      // Patch form with canonical details
      const nextTitle = d.title || this.form.value.title || '';
      this.form.patchValue({
        title: nextTitle,
        country_code: (d.country_code || 'US').toUpperCase(),
        city: d.city || '',
        latitude: d.latitude,
        longitude: d.longitude,
        place_external_id: d.place_external_id,
      });
      // Move map marker
      this.mapLat.set(d.latitude);
      this.mapLon.set(d.longitude);
    });
  }
  // ------------------------------------------------

  save() {
    if (this.form.invalid) return;
    const raw = this.form.getRawValue();
    const payload: TravelRecordCreate = {
      title: raw.title,
      notes: raw.notes || undefined,
      country_code: (raw.country_code || 'US').toUpperCase(),
      city: raw.city || undefined,
      latitude: Number(raw.latitude),
      longitude: Number(raw.longitude),
      destination_type: raw.destination_type as DestinationType,
      rating: Number(raw.rating),
      visited_at: raw.visited_at ? new Date(raw.visited_at).toISOString() : new Date().toISOString(),
      place_external_id: raw.place_external_id || undefined,
    };

    const id = this.editingId();
    const req = id ? this.api.update(id, payload) : this.api.create(payload);

    req.subscribe(() => {
      this.form.reset({
        title: '',
        notes: '',
        country_code: 'US',
        city: '',
        latitude: 0,
        longitude: 0,
        destination_type: 'CITY' as DestinationType,
        rating: 5,
        visited_at: new Date().toISOString(),
        place_external_id: '',
      });
      this.mapLat.set(0);
      this.mapLon.set(0);
      this.editingId.set(null);
      this.refresh();
    });
  }

  edit(r: TravelRecordRead) {
    this.editingId.set(r.id);
    this.form.patchValue(r as any);
    // Update map marker for edit
    this.mapLat.set(r.latitude);
    this.mapLon.set(r.longitude);
  }

  remove(id: number) {
    if (!confirm('Delete this entry?')) return;
    this.api.remove(id).subscribe(() => this.refresh());
  }

  onPhotoSelected(e: Event, recordId: number) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.api.uploadPhoto(recordId, file).subscribe(() => this.refresh());
  }
}
