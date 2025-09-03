import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  template: `
    <nav class="topnav">
      <a routerLink="/entries">Entries</a>
      <a routerLink="/insights">Insights</a>
      <a routerLink="/login" class="right">Logout</a>
    </nav>
    <router-outlet />
  `,
})
export class App {}
