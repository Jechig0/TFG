import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { environment } from '@environments/environment';
import { map, Observable, of, tap } from 'rxjs';
import { AsignaturaNota } from '../interfaces/pdfresponse.interface';
import { AlumnoStateService } from './alumno-state.service';

@Injectable({
  providedIn: 'root'
})
export class AlumnosService {

  apiUrl = environment.apiUrl

  private http = inject(HttpClient)
  alumnoStateService = inject(AlumnoStateService);

  // Obtiene las notas del alumno por su ID.
  getAlumnoById(id: string): Observable<[string, number][]> {
    return this.http.get<[string, number][]>(`${this.apiUrl}/alumno/${id}`).pipe(
      map((data) => {
        const resultado = data.map(([asignatura, nota]) => [asignatura, +nota] as [string, number]);
      return resultado;
    })
    );
  }

  // Obtiene la media del alumno por su ID.
  getMediaAlumno(id: string): Observable<string>{
    return this.http.get<string>(`${this.apiUrl}/alumno/${id}/media/`).pipe(
      map((media) => {
      // this.mediaAlumnos.update(prev => ({ ...prev, [id]: media }));
      return media;
    })
  );
  }

  // Verifica si el alumno existe en el sistema con el ID y DNI proporcionados.
  verificarAlumno(id: string, dni:string): Observable<string>{
    return this.http.post<{estado: string}>(`${this.apiUrl}/alumno/verificar`, {
      id_alumno: id.trim(),
      dni: dni.trim().toUpperCase()
    }).pipe(
      map(response => response.estado)
);


  }

  // Obtiene las asignaturas del alumno por su ID.
  getAsignaturas(id: string): Observable<string[][]>{
    return this.http.get<string[][]>(`${this.apiUrl}/asignatura/${id}`);
  }

  // Obtiene la probabilidad de acceso del alumno a una asignatura.
  getProbabilidadAcceso(id:string, asignatura: string): Observable<number>{
    asignatura = asignatura.replace(/\s+/g, '')
    return this.http.get<number>(`${this.apiUrl}/alumno/probabilidadEntrada/${id}/${asignatura}`)
  }

  // Obtiene la afinidad del alumno con una asignatura.
  getAfinidadAsignatura(id:string, asignatura: string): Observable<number>{
    asignatura = asignatura.replace(/\s+/g, '')
    return this.http.get<number>(`${this.apiUrl}/alumno/afinidad/${id}/${asignatura}`)
  }

  //Envía el informe PDF del expediente acafémico del alumno al backend para su procesamiento.
  enviarInformePdf(id: string, dni: string, file: File): Observable<AsignaturaNota[]> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dni', dni);

    return this.http.post<AsignaturaNota[]>(`${this.apiUrl}/alumno/${id}/subir-informe`, formData);
}

  // Elimina el expediente del alumno por su ID.
  eliminarAlumno(id:string): Observable<{estado: string}> {
    this.alumnoStateService.clear();
    return this.http.delete<{estado: string}>(`${this.apiUrl}/alumno/delete/${id}`);
  }
}
