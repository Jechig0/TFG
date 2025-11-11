import { Injectable } from '@angular/core';
import { sha256 } from 'js-sha256';

@Injectable({ providedIn: 'root' })
export class AlumnoStateService {

  setAlumno(id: string, dni: string) {
    sessionStorage.setItem("id_alumno", id.trim());
    sessionStorage.setItem("dni", sha256(dni.toUpperCase().trim()));
    sessionStorage.setItem("isAdmin", "false");
  }

  getId(): string | null {
    return sessionStorage.getItem("id_alumno");
  }

  getDni(): string | null {
    return sessionStorage.getItem("dni");
  }

  clear() {
    sessionStorage.removeItem("id_alumno");
    sessionStorage.removeItem("dni");
    sessionStorage.removeItem("isAdmin");
  }
}
