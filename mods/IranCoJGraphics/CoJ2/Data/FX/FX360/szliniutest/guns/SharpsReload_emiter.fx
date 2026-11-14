EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 0.9)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 3)
	}

	StartVelocity()
	{
		keyf(0, 60)
	}

	StartVelocityRand()
	{
		keyv(0, 40, 40, 40)
	}

	Direction()
	{
		keyv(0, 0, 0, 1)
	}

	GenArea("point")
}
