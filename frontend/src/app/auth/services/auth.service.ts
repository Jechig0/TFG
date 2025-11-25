import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { map, Observable, tap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {

  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  // Comprueba si el usuario actual es un administrador.
  checkAdmin(): boolean {
    return sessionStorage.getItem('isAdmin') === 'true';
  }

  // Intenta iniciar sesión con las credenciales proporcionadas.
  login(usuario: string, password: string): Observable<string> {
    const formData = new FormData();
    formData.append('user', usuario);
    formData.append('password', password);

    return this.http.post<{ message: string }>(`${this.apiUrl}/admin/check`, {
      user: usuario,
      password: password
    }).pipe(
      map(response => response.message),
      tap(response => {
        if (response === "Usuario autorizado") {
          sessionStorage.setItem('isAdmin', 'true');
        }
        else {
          sessionStorage.removeItem('isAdmin');
        }
      })
    );

  }
}
