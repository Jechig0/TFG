import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, tap } from 'rxjs';
import { environment } from '@environments/environment';
import { AsignaturaCount, AsignaturaCountRaw, Ponderacion } from '../interfaces/adminResponse.interface';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl;

  // Transforma la respuesta cruda en un formato más amigable
  private transformResponse(data: AsignaturaCountRaw[]): AsignaturaCount[] {
    return data.map(([nombre, count]) => ({ nombre, count }));
  }

  // Obtiene las asignaturas populares.
  getAsignaturasPopulares(): Observable<AsignaturaCount[]> {
    return this.http.get<AsignaturaCountRaw[]>(`${this.baseUrl}/admin/asignaturas_populares`)
      .pipe(map(this.transformResponse));
  }

  // Obtiene las media de afinidad por asignatura.
  getAsignaturasAfinidad(): Observable<AsignaturaCount[]> {
    return this.http.get<AsignaturaCountRaw[]>(`${this.baseUrl}/admin/asignaturas_afinidad`)
      .pipe(map(this.transformResponse));
  }

  // Obtiene la media de la probabilidad de acceso por asignatura.
  getAsignaturasProbabilidad(): Observable<AsignaturaCount[]> {
    return this.http.get<AsignaturaCountRaw[]>(`${this.baseUrl}/admin/asignaturas_probabilidad`)
      .pipe(map(this.transformResponse));
  }

  // Obtiene el conteo de consultas por titulaciones.
  getTitulaciones(): Observable<AsignaturaCount[]> {
    return this.http.get<AsignaturaCountRaw[]>(`${this.baseUrl}/admin/titulaciones`)
      .pipe(map(this.transformResponse));
  }

  // Reinicia los clusters en el sistema.
  resetClusters(): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.baseUrl}/admin/reiniciar_clusters`, {});
  }

  //Borra todos los expedientes del sistema.
  resetExpedientes(): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.baseUrl}/admin/reset_expedientes`, {});
  }

  // Borra todos los datos de consultas almacenadas.
  resetConsultas(): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.baseUrl}/admin/reset_consultas`, {});
  }

  // Obtiene las ponderaciones para la probabilidad de acceso.
  getPonderaciones(): Observable<Ponderacion[]> {
    return this.http.get<[string, number][]>(`${this.baseUrl}/admin/get_ponderaciones`)
    .pipe(
      map(arr => arr.map(([year, peso]) => ({ year, peso })))
    );
  }

  // Establece las ponderaciones para la probabilidad de acceso.
  setPonderaciones(payload: { ponderaciones: { year: string; peso: number }[] }): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.baseUrl}/admin/set_ponderaciones`, payload)
  }
}
