import { inject, Injectable, signal, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { LoginPayload, LoginResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private platformId = inject(PLATFORM_ID);
  private isBrowser = isPlatformBrowser(this.platformId);

  apiUrl = '/api/auth';
  private http = inject(HttpClient);

  token = signal<string | null>(
    this.isBrowser ? window.localStorage.getItem('token') : null
  );

  login(data: LoginPayload) {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, data);
  }

  setToken(t: string) {
    this.token.set(t);
    if (this.isBrowser) {
      window.localStorage.setItem('token', t);
    }
  }

  logout() {
    this.token.set(null);
    if (this.isBrowser) {
      window.localStorage.removeItem('token');
    }
  }

  isAuthed() {
    return !!this.token();
  }
}
