
    # @app.route('/actors/add')
    # def add_actor_form():
    #     form = AddActorForm()
    #     return render_template('pages/actors/add.html',form=form)


    # @app.route('/actors/add', methods=["POST"])
    # def add_actor():
    #     form = AddActorForm(request.form)
    #     added=False
    #     try:
    #         new_actor = Actors(
    #             name=form.name.data,
    #             age = form.age.data,
    #             gender = form.gender.data,
    #             is_available = form.is_available.data=="True"
    #         )
    #         db.session.add(new_actor)
    #         db.session.commit()
    #         added=True
    #     except:
    #         db.session.rollback()
    #     finally:
    #         db.session.close()

    #     if(added):
    #         flash('New Actor added successfully','success')
    #         return redirect(url_for('actors'))
    #     else:
    #         flash('Could not add new Actor','danger')
    #         return render_template('pages/actors/add.html',form=form)


    # @app.route('/actors/<int:actor_id>/edit')
    # def edit_actor_form(actor_id):   
    #     # check if requested actor id does exist
    #     actor = Actors.query.get(actor_id)     
    #     if(actor==None):
    #         # if not exist, return to actors list and flash an error
    #         flash('Requested Actor could not be found !!','danger')
    #         return redirect(url_for('actors'))
    #     # if exist, prepare form with actor info
    #     form = AddActorForm()
    #     form.name.data = actor.name
    #     form.age.data = actor.age
    #     form.gender.data = actor.gender
    #     form.is_available.data = "True" if actor.is_available else "False"
    #     return render_template('pages/actors/edit.html',form=form)


    # @app.route('/actors/<int:actor_id>/edit',methods=['POST'])
    # def edit_actor(actor_id):           
    #     form = AddActorForm(request.form)
    #     updated=False
    #     try:
    #         actor = Actors.query.get(actor_id)            
    #         actor.name=form.name.data,
    #         actor.age = form.age.data,
    #         actor.gender = form.gender.data,
    #         actor.is_available = form.is_available.data=="True"            
    #         db.session.commit()
    #         updated=True
    #     except:
    #         db.session.rollback()
    #     finally:
    #         db.session.close()

    #     if(updated):
    #         flash('Actor\'s info updated successfully','success')
    #         return redirect(url_for('actors'))
    #     else:
    #         flash('Could not update Actor\'s info','danger')
    #         return render_template('pages/actors/edit.html',form=form)


    # @app.route('/actors/<int:actor_id>/delete')
    # def delete_actor_form(actor_id):   
    #     # check if requested actor id does exist
    #     actor = Actors.query.get(actor_id)     
    #     if(actor==None):
    #         # if not exist, return to actors list and flash an error
    #         flash('Requested Actor could not be found !!','danger')
    #         return redirect(url_for('actors'))
    #     # if exist, prepare form with actor info
    #     return render_template('pages/actors/delete.html',actor=actor)


    # @app.route('/actors/<int:actor_id>/delete',methods=["POST"])
    # def delete_actor(actor_id):   
    #     # check if requested actor id does exist
    #     actor = Actors.query.get(actor_id)     
    #     if(actor==None):
    #         # if not exist, return to actors list and flash an error
    #         flash('Requested Actor could not be found !!','danger')
    #         return redirect(url_for('actors'))
    #     # if exist, delete and return to actors list
    #     elif(len(actor.movies) > 0):
    #         flash("Could not delete Actor, There is a related movie(s)!","danger")
    #         return render_template('pages/actors/delete.html',actor=actor)
    #     else:
    #         deleted=False
    #         try:
    #             db.session.delete(actor)
    #             db.session.commit()
    #             deleted=True
    #         except:
    #             db.session.rollback()
    #         finally:
    #             db.session.close()

    #         if(deleted):
    #             flash("Actor deleted successfully!","success")
    #             return redirect(url_for("actors"))
    #         else:
    #             flash("Could not delete Actor!","danger")
    #             return render_template('pages/actors/delete.html',actor=actor)



    # @app.route('/actors/<int:actor_id>')
    # def actor_info(actor_id):   
    #     # check if requested actor id does exist
    #     actor = Actors.query.get(actor_id)     
    #     if(actor==None):
    #         # if not exist, return to actors list and flash an error
    #         flash('Requested Actor could not be found !!','danger')
    #         return redirect(url_for('actors'))
    #     # if exist, prepare form with actor info
    #     return render_template('pages/actors/info.html',actor=actor)


    # @app.route('/movies')
    # def movies():
    #     movies = Movies.query.all()
    #     return render_template('pages/movies/list.html',movies=movies)


    # @app.route('/movies/add')
    # def add_movie_form():
    #     form = MovieForm()
    #     return render_template('pages/movies/add.html',form=form)


    # @app.route('/movies/add',methods=['POST'])
    # def add_movie():
    #     form = MovieForm(request.form)
    #     added=False
    #     movie_id=0
    #     try:
    #         new_movie = Movies(
    #             name = form.name.data,
    #             movie_status = form.movie_status.data,
    #             movie_category = form.movie_category.data,
    #             movie_rating = form.movie_rating.data
    #         )
    #         db.session.add(new_movie)
    #         db.session.commit()
    #         movie_id = new_movie.id
    #         added=True
    #     except:
    #         db.session.rollback()
    #     finally:
    #         db.session.close()
    #     if(added):
    #         flash("Movie added successfully","success")
    #         return redirect("/movies/{0}/actors".format(movie_id))
    #     else:
    #         flash("Could not add new movie!","danger")
    #         return render_template('pages/movies/add.html',form=form)

    # @app.route('/movies/<int:movie_id>')
    # def movie_info(movie_id):
    #     movie = Movies.query.get(movie_id)
    #     return render_template('pages/movies/info.html',movie=movie)

    # @app.route('/movies/<int:movie_id>/actors')
    # def movie_actors_form(movie_id):
    #     form = MovieActorsForm()        
    #     movie = Movies.query.get(movie_id)
    #     available_actors = Actors.query.filter(~Actors.id.in_([actor.id for actor in movie.actors])).all()
    #     form.Actor.choices = [(actor.id,actor.name) for actor in available_actors]
    #     return render_template('pages/movies/actors.html',movie=movie,form=form)
    
    # @app.route('/movies/<int:movie_id>/actors',methods=['POST'])
    # def movie_actors(movie_id):
    #     form = MovieActorsForm(request.form)        
    #     movie = Movies.query.get(movie_id)
    #     added=False
    #     try:
    #         actor_id = form.Actor.data
    #         actor_to_add = Actors.query.get(actor_id)
    #         movie.actors.append(actor_to_add)
    #         db.session.commit()
    #         added=True
    #     except:
    #         db.session.rollback()
    #     finally:
    #         db.session.close()
    #     if(added):
    #         flash("Actors added successfully","success")
    #     else:
    #         flash("Could not add Actor","danger") 
    #     movie = Movies.query.get(movie_id)
    #     available_actors = Actors.query.filter(~Actors.id.in_([actor.id for actor in movie.actors])).all()
    #     form.Actor.choices = [(actor.id,actor.name) for actor in available_actors]
    #     return render_template('pages/movies/actors.html',movie=movie,form=form)
    
    # @app.route('/movies/<int:movie_id>/actors',methods=['DELETE'])
    # def delete_movie_actors(movie_id):
    #     form = MovieActorsForm()        
    #     movie = Movies.query.get(movie_id)
    #     deleted=False
    #     try:
    #         actor_id = request.get_data("actor_id")
    #         actor_to_delete = Actors.query.get(actor_id)
    #         movie.actors.remove(actor_to_delete)
    #         db.session.commit()
    #         deleted=True
    #     except:
    #         db.session.rollback()
    #     finally:
    #         db.session.close()
    #     if(deleted):
    #         flash("Actors deleted successfully","success")
    #     else:
    #         flash("Could not delete Actor","danger") 
    #     movie = Movies.query.get(movie_id)
    #     available_actors = Actors.query.filter(~Actors.id.in_([actor.id for actor in movie.actors])).all()
    #     form.Actor.choices = [(actor.id,actor.name) for actor in available_actors]
    #     return render_template('pages/movies/actors.html',movie=movie,form=form)

  