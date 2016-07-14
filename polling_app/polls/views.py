from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from polls.models import Question, Choice
from django.template import RequestContext, loader 
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


 # Create your views here.

class IndexView(generic.ListView):

	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'
   
	def get_queryset(self):
		return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'

	def get_queryset(self):
		return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'

def vote(request, question_id):
	p=get_object_or_404(Question,pk=question_id)
	try:
		selected_choice = p.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		return render(request, 'polls/detail.html',{
			'question': p,
			'error_message': "You didn't select a choice.",
			})
	else:
		selected_choice.votes += 1
		selected_choice.save()
		sum = 0
		for q in p.choice_set.all():
			sum += float(q.votes)
		for q in p.choice_set.all():
			q.percent = float(q.votes)*100/float(sum)	
			q.save() 
		return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))

def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('polls:index')
    context = {
        "form": form,
    }
    return render(request, 'polls/registration_form.html', context)			


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'polls/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('polls:index')
            else:
                return render(request, 'polls/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'polls/login.html', {'error_message': 'Invalid login'})
    return render(request, 'polls/login.html')


