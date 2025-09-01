import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { environment } from '@environments/environment';
import { map, Observable, tap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {

  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl
  private _isAdmin = signal<boolean>(false);

  isAdmin = computed(() => this._isAdmin());

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
          this._isAdmin.set(true);
          sessionStorage.setItem('isAdmin', 'true');
        }
        else {
          this._isAdmin.set(false);
          sessionStorage.removeItem('isAdmin');
        }
      })
    );

  }
}
