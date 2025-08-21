import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {

  // true si el usuario está autenticado como admin
  private isAdminSubject = new BehaviorSubject<boolean>(false);
  isAdmin$ = this.isAdminSubject.asObservable();

  // Llamar al hacer login admin real
  setAdmin(value: boolean) {
    this.isAdminSubject.next(value);
  }

  // ejemplo: log out
  logout() {
    this.isAdminSubject.next(false);
  }
}
