import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AvgRating, TopDestinationPerMonth } from '../models';

@Injectable({ providedIn: 'root' })
export class AggregationsService {
  apiUrl = '/api/aggregation';
  private http = inject(HttpClient);
  base = `${this.apiUrl}/aggregations`;

  avgRatingByCountry() {
    return this.http.get<AvgRating[]>(`${this.base}/avg-rating-by-country`);
    // maps to [{ key, avg_rating, count }]
  }

  topDestinationPerMonth() {
    return this.http.get<TopDestinationPerMonth[]>(`${this.base}/top-destination-per-month`);
  }
}
