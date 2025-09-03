import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { RecordsPage, TravelRecordBase, TravelRecordRead } from '../models';


@Injectable({ providedIn: 'root' })
export class RecordsService {
apiUrl = '/api/travel_record';
  private http = inject(HttpClient);
  base = `${this.apiUrl}/records`;

  list(params: Record<string, any>) {
    let p = new HttpParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') p = p.set(k, String(v));
    });
    return this.http.get<RecordsPage>(this.base, { params: p });
  }

  get(id: number) {
    return this.http.get<TravelRecordRead>(`${this.base}/${id}`);
  }

  create(payload: TravelRecordBase) {
    return this.http.post<TravelRecordRead>(this.base, payload);
  }

  update(id: number, patch: Partial<TravelRecordBase>) {
    return this.http.patch<TravelRecordRead>(`${this.base}/${id}`, patch);
  }

  remove(id: number) {
    return this.http.delete<void>(`${this.base}/${id}`);
  }

  uploadPhoto(id: number, file: File) {
    const fd = new FormData();
    fd.append('file', file);
    return this.http.post(`${this.base}/${id}/photos`, fd);
  }

  listPhotos(id: number) {
    return this.http.get(`${this.base}/${id}/photos`);
  }

  deletePhoto(id: number, photoId: number) {
    return this.http.delete<void>(`${this.base}/${id}/photos/${photoId}`);
  }
}
