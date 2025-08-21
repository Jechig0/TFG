import { AuthService } from '@/auth/services/auth.service';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-login-page',
  imports: [RouterLink, ReactiveFormsModule],
  templateUrl: './admin-login-page.component.html',
})
export class AdminLoginPageComponent {

  authService = inject(AuthService)
  router = inject(Router)

  fb = inject(FormBuilder);
  hasError = signal(false)
  isPosting = signal(false)

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
  })
  //TODO: Arreglar el HTML de login
  onSubmit(){
    if(this.loginForm.invalid){
      this.hasError.set(true)
      setTimeout(() =>  {
        this.hasError.set(false)
      },2000)
      return
    }

    const {email = '', password = ''} = this.loginForm.value
    // this.authService.login(email!, password!)
    // .subscribe((isAuthenticated) =>{
    //   if(isAuthenticated){
    //     this.router.navigateByUrl('/')
    //     return;
    //   }
    //   this.hasError.set(true)
    //   setTimeout(() =>  {
    //     this.hasError.set(false)
    //   },2000)
    // })
  }
}