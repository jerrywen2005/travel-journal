import { Routes } from '@angular/router';
import { authGuard } from './auth/auth.guard';
import { LoginPage } from './auth/login.page';
import { EntriesPage } from './records/entries.page';
import { InsightsPage } from './aggregation/insights.page';

export const routes: Routes = [
  { path: 'login', component: LoginPage },
  { path: 'entries', component: EntriesPage, canActivate: [authGuard] },
  { path: 'insights', component: InsightsPage, canActivate: [authGuard] },
  { path: '', pathMatch: 'full', redirectTo: 'entries' },
  { path: '**', redirectTo: 'entries' },
];
