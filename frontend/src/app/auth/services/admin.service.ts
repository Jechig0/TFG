import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl;

  getAsignaturasPopulares(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/asignaturas_populares`);
  }

  getAsignaturasAfinidad(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/asignaturas_afinidad`);
  }

  getAsignaturasProbabilidad(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/asignaturas_probabilidad`);
  }

  getTitulaciones(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/titulaciones`);
  }
}