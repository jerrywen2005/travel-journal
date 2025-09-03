import { Component, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AggregationsService } from './aggregations.service';
import { RecordsService } from '../records/records.service';
import { AvgRating, TopDestinationPerMonth, RecordsPage, TravelRecordRead } from '../models';

@Component({
  standalone: true,
  selector: 'app-insights',
  imports: [CommonModule],
  templateUrl: './insights.page.html',
  styleUrls: ['./insights.page.css']
})
export class InsightsPage {
  private agg = inject(AggregationsService);
  private rec = inject(RecordsService);

  avg = signal<AvgRating[]>([]);
  top = signal<TopDestinationPerMonth[]>([]);
  records = signal<TravelRecordRead[]>([]);
  sortKey = signal<'rating'|'visited_at'|'title'>('visited_at');
  sortDir = signal<'asc'|'desc'>('desc');

  ngOnInit() {
    this.agg.avgRatingByCountry().subscribe(d => this.avg.set(d));
    this.agg.topDestinationPerMonth().subscribe(d => this.top.set(d));
    this.loadRecords();
  }

  loadRecords() {
    this.rec.list({ limit: 100, offset: 0, order_by: `${this.sortKey()}:${this.sortDir()}` })
      .subscribe((res: RecordsPage) => this.records.set(res.items));
  }

  setSort(key: 'rating'|'visited_at'|'title') {
    const dir = (this.sortKey() === key && this.sortDir() === 'desc') ? 'asc' : 'desc';
    this.sortKey.set(key);
    this.sortDir.set(dir);
    this.loadRecords();
  }
}
