import { Injectable } from '@angular/core';
import { sha256 } from 'js-sha256';

@Injectable({ providedIn: 'root' })
export class AlumnoStateService {

  // Guarda el ID y DNI del alumno en sessionStorage.
  setAlumno(id: string, dni: string) {
    sessionStorage.setItem("id_alumno", id.trim());
    sessionStorage.setItem("dni", sha256(dni.toUpperCase().trim()));
    sessionStorage.setItem("isAdmin", "false");
  }

  // Obtiene el ID del alumno desde sessionStorage.
  getId(): string | null {
    return sessionStorage.getItem("id_alumno");
  }

  // Obtiene el DNI del alumno desde sessionStorage.
  getDni(): string | null {
    return sessionStorage.getItem("dni");
  }

  // Limpia los datos del alumno almacenados en sessionStorage.
  clear() {
    sessionStorage.removeItem("id_alumno");
    sessionStorage.removeItem("dni");
    sessionStorage.removeItem("isAdmin");
  }
}
