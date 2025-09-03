export type ISO2 = string; // "US", "JP"...

export type DestinationType =
  | 'city' | 'nature' | 'beach' | 'museum' | 'park'
  | 'mountain' | 'desert' | 'historical' | 'food' | 'other';

export interface PhotoRead {
  id: number;
  file_path: string;
  content_type: string;
  size_bytes: number;
}



export interface TravelRecordBase {
  title: string;
  notes?: string | null;
  country_code: ISO2;
  region?: string | null;
  city?: string | null;
  latitude: number;
  longitude: number;
  destination_type: DestinationType;
  rating: number;
  visited_at: string; // ISO
  place_external_id?: string | null;
}

export interface TravelRecordRead extends TravelRecordBase {
  id: number;
  user_id: number;
  created_at: string;
  updated_at?: string | null;
  weather_summary?: string | null;
  photo?: PhotoRead | null;
}

export interface RecordsPage {
  items: TravelRecordRead[];
  total: number;
  limit: number;
  offset: number;
}

export interface AvgRating {
  key: string;
  avg_rating: number;
  count: number;
}

export interface TopDestinationPerMonth {
  month: string; // yyyy-mm-dd
  record_id: number;
  title: string;
  rating: number;
  city?: string | null;
  country_code: ISO2;
}

export type TravelRecordCreate = Omit<
  TravelRecordRead,
  'id' | 'user_id' | 'created_at' | 'updated_at' | 'weather_summary' | 'photo'
>;

export interface LoginPayload { email: string; password: string; }
export interface LoginResponse { access_token: string; }
