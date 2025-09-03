import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { RecordsService } from './records.service';
import { TravelRecordRead,DestinationType, TravelRecordCreate } from '../models';


@Component({
  standalone: true,
  selector: 'app-entries',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './entries.page.html',
  styleUrls: ['./entries.page.css']
})
export class EntriesPage {
  private fb = inject(FormBuilder);
  private api = inject(RecordsService);

  items = signal<TravelRecordRead[]>([]);
  total = signal(0);
  editingId = signal<number | null>(null);
  loading = signal(false);

  form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.maxLength(140)]],
    notes: [''],
    country_code: ['US', [Validators.required, Validators.pattern(/^[A-Z]{2}$/)]],
    city: [''],
    latitude: [0, [Validators.required, Validators.min(-90), Validators.max(90)]],
    longitude: [0, [Validators.required, Validators.min(-180), Validators.max(180)]],
    destination_type: 'CITY' as DestinationType,
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
    visited_at: raw.visited_at ? new Date(raw.visited_at).toISOString()
                               : new Date().toISOString(),
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
    this.editingId.set(null);
    this.refresh();
  });
}


  edit(r: TravelRecordRead) {
    this.editingId.set(r.id);
    this.form.patchValue(r as any);
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
