import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class PlacesService {
  private http = inject(HttpClient);
  apiUrl = '/api/places';

  autocomplete(q: string, sessionToken?: string) {
    let params = new HttpParams().set('q', q);
    if (sessionToken) params = params.set('session_token', sessionToken);
    return this.http.get<{ place_id: string; description: string }[]>(`${this.apiUrl}/autocomplete`, { params });
  }

  details(place_id: string) {
    const params = new HttpParams().set('place_id', place_id);
    return this.http.get<{
      place_external_id: string;
      title: string;
      country_code: string | null;
      city: string | null;
      latitude: number;
      longitude: number;
    }>(`${this.apiUrl}/details`, { params });
  }
}
