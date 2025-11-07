import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, tap } from 'rxjs';
import { environment } from '@environments/environment';
import { AsignaturaCount, AsignaturaCountRaw } from '../interfaces/adminResponse.interface';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl;

  private transformResponse(data: AsignaturaCountRaw[]): AsignaturaCount[] {
    return data.map(([nombre, count]) => ({ nombre, count }));
  }

  getAsignaturasPopulares(): Observable<AsignaturaCount[]> {
    return this.http.get<AsignaturaCountRaw[]>(`${this.baseUrl}/admin/asignaturas_populares`)
      .pipe(map(this.transformResponse));
  }

  getAsignaturasAfinidad(): Observable<AsignaturaCount[]> {
    return this.http.get<AsignaturaCountRaw[]>(`${this.baseUrl}/admin/asignaturas_afinidad`)
      .pipe(map(this.transformResponse));
  }

  getAsignaturasProbabilidad(): Observable<AsignaturaCount[]> {
    return this.http.get<AsignaturaCountRaw[]>(`${this.baseUrl}/admin/asignaturas_probabilidad`)
      .pipe(map(this.transformResponse));
  }

  getTitulaciones(): Observable<AsignaturaCount[]> {
    return this.http.get<AsignaturaCountRaw[]>(`${this.baseUrl}/admin/titulaciones`)
      .pipe(map(this.transformResponse));
  }

  resetClusters(): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.baseUrl}/admin/reiniciar_clusters`, {});
  }

  setPonderaciones(ponderaciones: {
    expediente: number;
    historial: number;
    demanda: number;
  }): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.baseUrl}/admin/ponderaciones`, ponderaciones);
  }
}
