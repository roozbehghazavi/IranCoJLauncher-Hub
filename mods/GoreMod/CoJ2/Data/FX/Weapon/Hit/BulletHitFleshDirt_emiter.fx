EmiterDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}


	GenType ("one_time")
	NumParticles()
	{
		keyf(0, 30)
	}

	StartVelocity()
	{
		keyf(0, 330)
	}

	StartVelocityRand()
	{
		keyv(0, 40, 420, 40)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}


	GenArea("point")

	Span()
	{
		keyv(0, 0,0,0)
	}
}