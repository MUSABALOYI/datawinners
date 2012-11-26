var questionnaireViewModel =
{
    questions : ko.observableArray([]),
    hasAddedNewQuestions : false,
    hasDeletedOldQuestion : false,
    language:'en',

    addQuestion : function() {
        var question = new DW.question();
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        question.newly_added_question(true);
        DW.check_question_type_according_radio_button(question.type());
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.selectedQuestion(question);
        DW.init_question_constraints();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        DW.charCount();
        questionnaireViewModel.hasAddedNewQuestions = true;
        DW.questionnaire_was_changed = true;
    },
    loadQuestion: function(question) {
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        
        DW.check_question_type_according_radio_button(question.type());
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.questions.valueHasMutated();
    },
    renumberQuestions: function(){
        var questionPattern = /^Question \d+$/;
        for (var i = 0; i < questionnaireViewModel.questions().length; i++){
            var question = questionnaireViewModel.questions()[i];
            if (questionPattern.test(question.title()) )
                question.title("Question " + (i + 1));
        }
    },
    removeQuestion: function(question) {
        var index = $.inArray(question, questionnaireViewModel.questions());
        if (!question.newly_added_question()) {
            questionnaireViewModel.hasDeletedOldQuestion = true;
            DW.questionnaire_was_changed = true;
        }
        questionnaireViewModel.questions.remove(question);
        if(questionnaireViewModel.questions().length == 0){
            questionnaireViewModel.addQuestion();
            return;
        }
        questionnaireViewModel.renumberQuestions();
        var next_index = (index) % questionnaireViewModel.questions().length;
        questionnaireViewModel.changeSelectedQuestion(questionnaireViewModel.questions()[next_index]);
        questionnaireViewModel.hasAddedNewQuestions = true;
    },
    removeIfQuestionIsSelectedQuestion: function(question) {
        if (questionnaireViewModel.selectedQuestion() == question) {
            questionnaireViewModel.removeQuestion(question);
        }
    },
    showAddChoice:function() {
        if (questionnaireViewModel.selectedQuestion().isAChoiceTypeQuestion() == "choice") {
            if (questionnaireViewModel.selectedQuestion().choices().length == 0) {
                questionnaireViewModel.addOptionToQuestion();
                questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
            }
            return true;
        }
        return false;
    },
    showDateFormats:function() {
        return questionnaireViewModel.selectedQuestion().type() == "date";
    },
    showAddRange:function() {
        return questionnaireViewModel.selectedQuestion().type() == 'integer';
    },
    showAddTextLength:function() {
        return questionnaireViewModel.selectedQuestion().type() == 'text';
    },
    addOptionToQuestion: function() {
        var selectedQuestionCode = "a";
        if (questionnaireViewModel.selectedQuestion().choices().length > 0) {
            var lastChoice = questionnaireViewModel.selectedQuestion().choices()[questionnaireViewModel.selectedQuestion().choices().length - 1];
            selectedQuestionCode = DW.next_option_value(lastChoice.val);
        }
        questionnaireViewModel.selectedQuestion().choices.push({text:"", val:selectedQuestionCode});
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
    },
    removeOptionFromQuestion:function(choice) {
        var choices = questionnaireViewModel.selectedQuestion().choices();
        var indexOfChoice = $.inArray(choice, choices);
        var lastChoiceValue = choice['val'];//.charCodeAt(0);
        var i = indexOfChoice + 1;
        for(i; i < choices.length; i=i+1){
            choices[i]['val'] = lastChoiceValue;
            $("span.bullet", $("#options_list li").eq(i)).html(lastChoiceValue + ".");
            lastChoiceValue = DW.next_option_value(lastChoiceValue);//lastChoiceValue + 1;
        }
        questionnaireViewModel.selectedQuestion().choices.remove(choice);
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
    },
    selectedQuestion: ko.observable({}),
    changeSelectedQuestion: function(question) {
        DW.check_question_type_according_radio_button(question.type());
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        $(this).addClass("question_selected");
        DW.close_the_tip_on_period_question();
    },
    set_old_values: function(question){
        if(question){
            DW.option_warning_dialog.old_question_type = question.type();
        }
    },
    remove_option: function(choice){
        var choices = questionnaireViewModel.selectedQuestion().options.choices;
        var choice_values = $(choices).map(function(index, choice){
            return choice.val;
        });

        if(is_edit){
            if($.inArray(choice.val, choice_values) != -1){ DW.questionnaire_was_changed = true; }
        }
        questionnaireViewModel.removeOptionFromQuestion(choice);
    },
    changeQuestionType: function(type_selector) {
        var type = questionnaireViewModel.selectedQuestion().type();
        var choices = questionnaireViewModel.selectedQuestion().choices();
        var type_equal = type_selector.value == type
            || (type_selector.value == 'choice' && (type.indexOf('select') >= 0));
        if (typeof(is_edit) == "undefined" || !is_edit || questionnaireViewModel.selectedQuestion().newly_added_question()) {
            DW.init_question_constraints();
            DW.change_question_type_for_selected_question(type_selector.value);
            return;
        } else if (type_equal){
            return;
        }
        DW.option_warning_dialog.show_warning(gettext("You have changed the Answer Type.<br>If you have previously collected data, it may be rendered incorrect.<br><br>Are you sure you want to continue?"));
        DW.option_warning_dialog.cancelEventHandler = function(){
            try {
                questionnaireViewModel.selectedQuestion().type(type);
                questionnaireViewModel.selectedQuestion().choices(choices);
            } catch (e) {}
            if (type.indexOf('select') != -1) type = 'choice';
            $("[name='type'][value='" + type + "']").attr('checked', true);
            DW.option_warning_dialog.continueEventHandler = function(){};
        };
        DW.option_warning_dialog.continueEventHandler = function(){
            var new_type = $("input[name='type']:checked").val();
            DW.init_question_constraints();
            DW.change_question_type_for_selected_question(new_type);
            DW.questionnaire_was_changed = true;
        };
    },
    showLengthLimiter: function() {
        return questionnaireViewModel.selectedQuestion().length_limiter() == 'length_limited';
    },
    set_all_questions_as_old_questions:function(){
        for (var question_index in questionnaireViewModel.questions()){
            questionnaireViewModel.questions()[question_index].newly_added_question(false)
        }
    },
    choiceCanBeDeleted: function() {
        return questionnaireViewModel.selectedQuestion().choices().length > 1 && questionnaireViewModel.isEnabled();
    },
    isEnabled: function(){
        if($("#not_wizard").length>0){
            return questionnaireViewModel.selectedQuestion().isEnabled();
        }
        else{
            return true;
        }
    },
    isTypeEnabled: function(){
        return questionnaireViewModel.isEnabled() && !questionnaireViewModel.selectedQuestion().event_time_field_flag();
    }
};